import json
import ollama
import uuid
import sys
from datetime import datetime
import os

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def save_output(output_data, output_filepath):
    """Save generated output to a JSON file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

def parse_embedded_json(node):
    """
    Recursively check if the 'step' field contains embedded JSON.
    If so, parse it and update the node's 'children' accordingly.
    """
    # If 'step' is a string that looks like JSON, try to parse it.
    step_value = node.get("step", "")
    if isinstance(step_value, str) and (step_value.strip().startswith('[') or step_value.strip().startswith('{')):
        try:
            parsed = json.loads(step_value)
            # If parsed is a list, replace the children with parsed nodes
            if isinstance(parsed, list):
                new_children = []
                for item in parsed:
                    if isinstance(item, dict):
                        new_children.append(item)
                    else:
                        new_children.append({"step": str(item), "children": []})
                node["children"] = new_children
                # Don't clear the step field completely to avoid empty steps
                if not node.get("title"):
                    node["title"] = step_value
            elif isinstance(parsed, dict):
                node["children"] = [parsed]
                if not node.get("title"):
                    node["title"] = step_value
        except json.JSONDecodeError:
            # If parsing fails, leave the node unchanged.
            pass

    # Recursively process all children.
    for child in node.get("children", []):
        parse_embedded_json(child)
    return node

def chat_with_llm(model, system_message, user_message, parameters=None):
    """Generic function to interact with LLMs via Ollama."""
    if parameters is None:
        parameters = {}
    
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        options=parameters
    )
    return response["message"]["content"].strip()

def clean_llm_json_response(response_text):
    """Clean an LLM response to extract valid JSON."""
    # Remove markdown code blocks
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    return response_text

def parse_llm_json_response(response_text, include_children=False):
    """Parse JSON from an LLM response with fallback handling.
    
    Args:
        response_text: The text response from the LLM
        include_children: Whether to include empty children arrays for hierarchical data
    """
    cleaned_text = clean_llm_json_response(response_text)
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fallback: return each line as a separate item
        if include_children:
            return [{"step": s.strip(), "children": []} 
                    for s in cleaned_text.split("\n") 
                    if s.strip() and not s.strip().startswith('#')]
        else:
            return [{"step": s.strip()} 
                    for s in cleaned_text.split("\n") 
                    if s.strip() and not s.strip().startswith('#')]

def create_output_metadata(task_name, start_time, output_uuid=None):
    """Create standard metadata for output files."""
    end_time = datetime.now()
    time_taken = end_time - start_time
    
    # No need to generate UUID here, it should be passed from get_output_filepath
    # or generated at a higher level
    return {
        "uuid": output_uuid,
        "date_created": end_time.isoformat(),
        "task": task_name,
        "time_taken": str(time_taken)
    }

def get_output_filepath(output_dir, output_uuid=None, specified_path=None):
    """Determine output filepath based on arguments or generate a default one."""
    if specified_path:
        return specified_path, output_uuid
        
    # Create a UUID for this output if not provided
    if output_uuid is None:
        output_uuid = str(uuid.uuid4())
    
    os.makedirs(f"output/{output_dir}", exist_ok=True)
    return f"output/{output_dir}/{output_uuid}.json", output_uuid

def handle_command_args(usage_msg, min_args=1, max_args=2):
    """Process command line arguments with validation."""
    if len(sys.argv) > max_args + 1 or len(sys.argv) < min_args + 1:
        print(usage_msg)
        sys.exit(1)
        
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2] if len(sys.argv) > 2 else None
    
    return input_filepath, output_filepath