import json
import sys
import os
from datetime import datetime
from uno_utils import (
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
    
    for i, child in enumerate(tree.get("children", [])):
        found, child_path = find_node_by_step_text(child, step_text, path + [i])
        if found:
            return found, child_path
    
    return None, None

def expand_node(node, model, parameters=None, depth=1, replace_existing=True, num_substeps=None):
    """Expand a node into more detailed substeps."""
    if parameters is None:
        parameters = {}
    
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
    
    # Parse the LLM response with children arrays for hierarchical data
    substeps = parse_llm_json_response(response_text, include_children=True)
    
    if not isinstance(substeps, list):
        substeps = [{"step": "No valid substeps could be generated", "children": []}]
    
    # Copy the node to avoid modifying the original
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
    
    # Create a copy of the tree to avoid modifying the original
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

def main():
    """Main function to run the node expansion routine."""
    usage_msg = "Usage: python expand-node.py <input_json> [output_json]"
    input_filepath, specified_output_filepath = handle_command_args(usage_msg)
    
    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    tree = input_data.get("tree", {})
    node_path = input_data.get("node_path", [])
    node_step = input_data.get("node_step", None)
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})
    depth = input_data.get("depth", 1)
    replace_existing = input_data.get("replace_existing", True)
    num_substeps = input_data.get("num_substeps", None)
    
    # Find the node to expand
    target_node = None
    node_path_in_tree = []
    
    if node_path:
        target_node, node_path_in_tree = find_node_by_path(tree, node_path)
    elif node_step:
        target_node, node_path_in_tree = find_node_by_step_text(tree, node_step)
    
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
    metadata = create_output_metadata("Node Expansion", start_time, output_uuid)
    
    # Combine metadata with the updated tree
    output_data = {
        **metadata,
        "tree": updated_tree,
        "expanded_node_path": node_path_in_tree,
        "expanded_node_step": target_node.get("step", "")
    }
    
    save_output(output_data, output_filepath)
    print(f"Node expanded, updated tree saved to {output_filepath}")

if __name__ == "__main__":
    main()