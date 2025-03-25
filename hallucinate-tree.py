import json
import ollama
import sys
import uuid
from datetime import datetime

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def parse_embedded_json(node):
    """
    Recursively check if the 'step' field contains embedded JSON.
    If so, parse it and update the node's 'children' accordingly,
    then clear the 'step' field to avoid duplication.
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
                # Clear the 'step' field as its content is now in children
                node["step"] = ""
            elif isinstance(parsed, dict):
                node["children"] = [parsed]
                node["step"] = ""
        except json.JSONDecodeError:
            # If parsing fails, leave the node unchanged.
            pass

    # Recursively process all children.
    for child in node.get("children", []):
        parse_embedded_json(child)
    return node

def generate_task_tree(input_data):
    """Generate a structured task tree using AI hallucinations."""
    task = input_data.get("task", "Unknown Task")
    depth = input_data.get("depth", 2)  # Default depth of 2
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})

    systemMsg = (
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

        prompt = (
            "Break down the following task into 3-7 sub-steps. "
            f"Task: {step}\n\n"
            "Return ONLY a JSON array of step objects, with no markdown formatting, code blocks, or extra text."
        )
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": systemMsg},
                {"role": "user", "content": prompt}
            ],
            options=parameters
        )

        response_text = response["message"]["content"].strip()
        
        # Strip any markdown code block indicators
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            # Try to parse the entire response as JSON
            parsed_steps = json.loads(response_text)
            
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
                
        except json.JSONDecodeError:
            # Fallback: split by lines as before
            substeps = [s.strip() for s in response_text.split("\n") if s.strip()]
            return {"step": step, "children": [{"step": s, "children": []} for s in substeps]}

    tree = expand_step(task, 0)
    return tree

def save_output(output_data, output_filepath):
    """Save generated output to a JSON file."""
    with open(output_filepath, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

def main():
    """Main function to run the hallucination-based tree generation."""
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python generate_tree.py <input_json> [output_json]")
        sys.exit(1)
    if len(sys.argv) == 3:
        output_filepath = sys.argv[2]
    print("Working...")
    start_time = datetime.now()
    input_filepath = sys.argv[1]

    input_data = load_json(input_filepath)
    output_content = generate_task_tree(input_data)
    end_time = datetime.now()

    print("RESPONSE: " + str(output_content))

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)
    date_time_str = end_time.isoformat()

    # Get a UUID for this output
    output_uuid = str(uuid.uuid4())
    if len(sys.argv) == 2:
        output_filepath = "output/hallucinate-tree/" + output_uuid + ".json"
    else:
        output_filepath = sys.argv[3]

    output_data = {
        "uuid": output_uuid,
        "date_created": date_time_str,
        "task": "Hallucinate Tree",
        "time_taken": time_taken_str,
        "tree": output_content
    }

    save_output(output_data, output_filepath)
    print(f"Generated initial tree, output saved to {output_filepath}")

if __name__ == "__main__":
    main()
