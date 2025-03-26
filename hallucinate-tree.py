import os
import json
import sys
import uuid
import re
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args
)

def sanitize_filename(name):
    """Convert a step name to a valid directory name using lowercase and underscores."""
    # Convert to lowercase
    sanitized = name.lower()
    # Remove invalid characters and replace spaces/hyphens with underscores
    sanitized = re.sub(r'[^\w\s-]', '', sanitized)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    # Ensure it's not too long
    return sanitized[:40]  # Shortened to leave room for the UUID

def save_tree_to_filesystem(tree, base_path):
    """Save a tree structure to the filesystem where each node is a directory."""
    # Create the base directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    
    # Generate UUID for this node if it doesn't have one
    if "uuid" not in tree:
        tree["uuid"] = str(uuid.uuid4())
    
    # Save the node's details as node.json
    node_details = {
        "step": tree["step"],
        "uuid": tree["uuid"]
    }
    with open(os.path.join(base_path, "node.json"), "w", encoding="utf-8") as f:
        json.dump(node_details, f, indent=4)
    
    # Create child directories for each child node
    for child in tree.get("children", []):
        # Generate UUID for the child if it doesn't have one
        if "uuid" not in child:
            child["uuid"] = str(uuid.uuid4())
        
        # Create directory name: sanitized_name_uuid
        child_name = sanitize_filename(child["step"])
        
        # If sanitizing results in an empty string, use a generic name
        if not child_name:
            child_name = "step"
            
        # Append the UUID (shortened for readability)
        short_uuid = child["uuid"].split('-')[0]  # Take just first segment
        dir_name = f"{child_name}_{short_uuid}"
        
        # Check if the directory already exists (should be unlikely with UUIDs)
        child_path = os.path.join(base_path, dir_name)
        if os.path.exists(child_path):
            # In the unlikely case of a collision, use the full UUID
            dir_name = f"{child_name}_{child['uuid']}"
            child_path = os.path.join(base_path, dir_name)
            
        save_tree_to_filesystem(child, child_path)
    
    return base_path

def generate_task_tree(input_data):
    """Generate a structured task tree using AI hallucinations."""
    task = input_data.get("task", "Unknown Task")
    depth = input_data.get("depth", 2)  # Default depth of 2
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})

    system_msg = (
        "You are an AI that breaks down complex tasks into hierarchical steps. "
        "For each task, generate a set of sub-steps needed to complete it. "
        "Maintain clarity and logical order. "
        "Format your response as a valid JSON array of step objects, where each object has a 'step' field "
        "and optionally a 'children' array containing substeps. "
        "Example format: [{'step': 'Main step 1', 'children': [{'step': 'Substep 1.1'}, {'step': 'Substep 1.2'}]}, {'step': 'Main step 2'}] "
        "Your entire response must be parseable as JSON. Do not include markdown formatting, code blocks, or commentary."
    )

    def expand_step(step, current_depth):
        if current_depth >= depth:
            return {"step": step, "children": []}

        user_msg = (
            "Break down the following task into 3-7 sub-steps. "
            f"Task: {step}\n\n"
            "Return ONLY a JSON array of step objects, with no markdown formatting, code blocks, or extra text."
        )
        
        # Use chat_with_llm instead of direct ollama.chat
        response_text = chat_with_llm(model, system_msg, user_msg, parameters)
        
        try:
            # Use parse_llm_json_response utility with include_children=True for hierarchical data
            parsed_steps = parse_llm_json_response(response_text, include_children=True)
            
            if isinstance(parsed_steps, list):
                # Process each step recursively if we're not at max depth
                if current_depth + 1 < depth:
                    for substep in parsed_steps:
                        if isinstance(substep, dict) and "step" in substep and "children" not in substep:
                            substep_text = substep["step"]
                            child_tree = expand_step(substep_text, current_depth + 1)
                            substep["children"] = child_tree.get("children", [])
                return {"step": step, "children": parsed_steps}
            else:
                # If response isn't a list, create a simple step
                return {"step": step, "children": []}
                
        except Exception as e:
            print(f"Error processing response: {e}")
            # Fallback: create a simple structure
            return {"step": step, "children": [{"step": response_text, "children": []}]}

    tree = expand_step(task, 0)
    # Generate UUID for root node
    tree["uuid"] = str(uuid.uuid4())
    return tree

def main():
    """Main function to run the hallucination-based tree generation."""
    usage_msg = "Usage: python hallucinate-tree.py <input_json> [output_dir]"
    
    # Use handle_command_args utility
    input_filepath, specified_output_path = handle_command_args(usage_msg)

    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    tree_content = generate_task_tree(input_data)
    
    # Generate a UUID for this tree
    tree_uuid = tree_content["uuid"]
    
    # Define the base output directory
    if specified_output_path:
        # If output path is specified, use that
        base_output_dir = specified_output_path
    else:
        # Otherwise create a directory with the UUID in the default location
        base_output_dir = os.path.join("output", "hallucinate-tree", tree_uuid)
    
    # Create the base output directory if it doesn't exist
    os.makedirs(base_output_dir, exist_ok=True)
    
    # Save metadata to the base directory
    metadata = create_output_metadata("Hallucinate Tree", start_time, tree_uuid)
    with open(os.path.join(base_output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    # Save the tree structure to the filesystem
    tree_root_dir = save_tree_to_filesystem(tree_content, base_output_dir)
    
    print(f"Generated initial tree, output saved to {tree_root_dir}")

if __name__ == "__main__":
    main()
