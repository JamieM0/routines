import os
import json
import sys
import uuid
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args
)

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
    return tree

def main():
    """Main function to run the hallucination-based tree generation."""
    usage_msg = "Usage: python hallucinate-tree.py <input_json> [output_json]"
    
    # Use handle_command_args utility
    input_filepath, specified_output_filepath = handle_command_args(usage_msg)

    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    tree_content = generate_task_tree(input_data)
    
    print("RESPONSE: " + str(tree_content))
    
    # Use get_output_filepath and create_output_metadata utilities
    output_filepath, output_uuid = get_output_filepath(
        "hallucinate-tree", 
        specified_path=specified_output_filepath
    )
    
    metadata = create_output_metadata("Hallucinate Tree", start_time, output_uuid)
    
    # Combine metadata and tree into output data
    output_data = {**metadata, "tree": tree_content}
    
    # Save output using utility
    save_output(output_data, output_filepath)
    
    print(f"Generated initial tree, output saved to {output_filepath}")

if __name__ == "__main__":
    main()
