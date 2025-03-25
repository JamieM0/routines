import json
import sys
import os
import re
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args
)

def find_node_by_path(tree, path):
    """Find a node in the tree using a path of indices."""
    if not path:
        return tree, []
    
    current = tree
    current_path = []
    
    for index in path:
        if not isinstance(index, int) or "children" not in current or index >= len(current["children"]):
            return None, []
        current = current["children"][index]
        current_path.append(index)
    
    return current, current_path

def find_node_by_step_text(tree, step_text, path=None):
    """Find a node in the tree by matching the step text."""
    if path is None:
        path = []
    
    if tree.get("step") == step_text:
        return tree, path
    
    # Handle case where node doesn't have children array yet
    children = tree.get("children", [])
    for i, child in enumerate(children):
        found, child_path = find_node_by_step_text(child, step_text, path + [i])
        if found:
            return found, child_path
    
    return None, None

def normalize_tree_for_expansion(tree):
    """Ensure all nodes in the tree have a children property."""
    if isinstance(tree, dict):
        if "step" in tree and "children" not in tree:
            tree["children"] = []
        if "children" in tree:
            for child in tree["children"]:
                normalize_tree_for_expansion(child)
    return tree

def expand_node(node, model, parameters=None, depth=1, replace_existing=True, num_substeps=None):
    """Expand a node into more detailed substeps."""
    if parameters is None:
        parameters = {}
    
    # Ensure node has a children property before expansion
    if "children" not in node:
        node["children"] = []
    
    # Allow customizing the number of substeps
    substep_range = "3-7" if num_substeps is None else str(num_substeps)
    
    system_msg = (
        "You are an AI that breaks down tasks into detailed steps. "
        "For the given task, generate a set of specific, actionable substeps needed to complete it. "
        "Maintain clarity and logical order. "
        "Format your response as a valid JSON array of step objects, where each object has a 'step' field. "
        "Example format: [{'step': 'First detailed step'}, {'step': 'Second detailed step'}] "
        "Your entire response must be parseable as JSON. Do not include markdown formatting or commentary."
    )
    
    user_msg = (
        f"Break down the following task into {substep_range} detailed substeps:\n\n"
        f"Task: {node.get('step', 'Unknown Task')}\n\n"
        "Return ONLY a JSON array of step objects, with no markdown formatting, code blocks, or extra text."
    )
    
    response_text = chat_with_llm(model, system_msg, user_msg, parameters)
    
    # Parse the LLM response with include_children=True for hierarchical data
    substeps = parse_llm_json_response(response_text, include_children=True)
    
    if not isinstance(substeps, list):
        substeps = [{"step": "No valid substeps could be generated", "children": []}]
    
    # Clone the node to avoid modifying the original
    expanded_node = {**node}
    
    # Update the children based on the replace_existing flag
    if replace_existing or "children" not in node or not node["children"]:
        expanded_node["children"] = substeps
    else:
        # Merge with existing children
        expanded_node["children"] = expanded_node.get("children", []) + substeps
    
    return expanded_node

def update_tree_at_path(tree, path, new_node):
    """Update the tree by replacing a node at the given path."""
    if not path:  # We're updating the root node
        return new_node
    
    # Create a deep copy of the tree to avoid modifying the original
    updated_tree = json.loads(json.dumps(tree))
    
    # Navigate to the parent of the target node
    current = updated_tree
    for i in range(len(path) - 1):
        index = path[i]
        if "children" not in current or index >= len(current["children"]):
            # Path is invalid, return original tree
            return tree
        current = current["children"][index]
    
    # Replace the target node with the new node
    last_index = path[-1]
    if "children" not in current or last_index >= len(current["children"]):
        # Path is invalid, return original tree
        return tree
    
    current["children"][last_index] = new_node
    
    return updated_tree

def parse_path_string(path_str):
    """Convert a path string like '1-0-2' or '4' to a list of integers [1, 0, 2] or [4]."""
    try:
        # Handle both dash-separated paths and single numbers
        if '-' in path_str:
            return [int(i) for i in path_str.split('-')]
        else:
            return [int(path_str)]
    except ValueError:
        return None

def handle_expand_node_args():
    """Custom argument handling for expand-node.py to support node path specification."""
    usage_msg = "Usage: python expand-node.py <input_json> [node_path] [output_json]\nExample: python expand-node.py input.json 1-0-2 output.json"
    
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print(usage_msg)
        sys.exit(1)
        
    input_filepath = sys.argv[1]
    node_path_str = None
    output_filepath = None
    
    # Process the second argument - could be a node path or output filepath
    if len(sys.argv) >= 3:
        arg2 = sys.argv[2]
        # If it doesn't end with .json and can be parsed as a number or contains dashes
        # treat it as a node path
        if not arg2.endswith('.json') and (arg2.replace('-', '').isdigit() or '-' in arg2):
            node_path_str = arg2
        else:
            output_filepath = arg2
    
    # Process the third argument - must be output filepath
    if len(sys.argv) >= 4:
        output_filepath = sys.argv[3]
    
    return input_filepath, node_path_str, output_filepath

def main():
    """Main function to run the node expansion routine."""
    input_filepath, node_path_str, specified_output_filepath = handle_expand_node_args()
    
    print("Working...")
    start_time = datetime.now()
    
    # Load input data
    input_data = load_json(input_filepath)
    
    # Handle both standard input format and output file format
    # If the input file is an output file, extract the tree from it
    if isinstance(input_data, dict) and "tree" in input_data and isinstance(input_data["tree"], dict):
        tree = input_data["tree"]
        # Also extract other useful parameters if they exist
        model = input_data.get("model", "gemma3")
    else:
        tree = input_data.get("tree", input_data)
        model = input_data.get("model", "gemma3")
    
    # Normalize the tree specifically for expansion
    tree = normalize_tree_for_expansion(tree)
    
    # Get node path from command line or input data
    node_path = None
    if node_path_str:
        node_path = parse_path_string(node_path_str)
    else:
        node_path = input_data.get("node_path", [])
    
    node_step = input_data.get("node_step", None)
    
    # Extract parameters from input if available
    parameters = input_data.get("parameters", {})
    depth = input_data.get("depth", 1)
    replace_existing = input_data.get("replace_existing", True)
    num_substeps = input_data.get("num_substeps", None)
    
    # Find the node to expand
    target_node = None
    node_path_in_tree = []
    
    # If no node is specified or not found by path_str, try to handle gracefully
    if node_path:
        print(f"Searching for node at path: {node_path}")
        target_node, node_path_in_tree = find_node_by_path(tree, node_path)
        
        # Debug info if node not found
        if not target_node:
            print(f"WARNING: Node at path {node_path} not found.")
            print(f"Available paths at root level: 0 to {len(tree.get('children', [])) - 1}")
    elif node_step:
        print(f"Searching for node with text: '{node_step}'")
        target_node, node_path_in_tree = find_node_by_step_text(tree, node_step)
    else:
        # If no node is specified, default to expanding the root node
        print("No node specified, expanding the root node.")
        target_node, node_path_in_tree = tree, []
        
        # Alternative: Let the user choose a node interactively
        # print_tree_nodes(tree)
        # node_choice = input("Enter the number of the node to expand: ")
        # ...
    
    if not target_node:
        print(f"Error: Could not find the specified node in the tree.")
        sys.exit(1)
    
    print(f"Expanding node: '{target_node.get('step', 'Unknown')}'")
    
    # Expand the node
    expanded_node = expand_node(
        target_node, 
        model, 
        parameters, 
        depth, 
        replace_existing,
        num_substeps
    )
    
    # Update the tree with the expanded node
    updated_tree = update_tree_at_path(tree, node_path_in_tree, expanded_node)
    
    # Get output filepath and UUID
    output_filepath, output_uuid = get_output_filepath(
        "expand-node",
        specified_path=specified_output_filepath
    )
    
    # Create metadata
    metadata = create_output_metadata("Node Expansion", start_time, output_uuid)
    
    # Combine metadata with the updated tree
    output_data = {
        **metadata,
        "tree": updated_tree,
        "expanded_node_path": node_path_in_tree,
        "expanded_node_step": target_node.get("step", "")
    }
    
    # Double-check output_filepath is valid before trying to save
    if not output_filepath:
        output_filepath = f"output/expand-node/{uuid.uuid4()}.json"
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        print(f"Using default output filepath: {output_filepath}")
    
    save_output(output_data, output_filepath)
    print(f"Node expanded, updated tree saved to {output_filepath}")

if __name__ == "__main__":
    main()