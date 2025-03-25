import json
import ollama
import sys
import uuid
from datetime import datetime

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_summary(input_data):
    """Summarise the input text"""
    prompt = f"Summarize the following text concisely:\n\n{input_data.get('input_text')}"

    if "output_format" in input_data:
        prompt += f"\n\nProvide output as: {input_data['output_format']}"

    if "success_criteria" in input_data:
        criteria_str = json.dumps(input_data["success_criteria"], indent=2)
        prompt += f"\n\nSuccess Criteria:\n{criteria_str}"

    systemMsg = (
        "You are an AI assistant specialized in summarizing content. "
        "Your goal is to provide a concise and clear summary of the provided text. "
        "Ensure that the summary captures the key points, main ideas, and critical details. "
        "Keep the summary brief, precise, and easy to understand. "
        "Avoid unnecessary details or opinions. "
        "Follow the output format as specified by the user if provided; otherwise, return a plain text summary."
    )

    response = ollama.chat(
        model=input_data["model"],
        messages=[{"role": "system", "content": systemMsg},
                  {"role": "user", "content": prompt}],
        options=input_data.get("parameters", {})
    )

    return response["message"]["content"]

def save_output(output_data, output_filepath):
    """Save generated output to a JSON file."""
    with open(output_filepath, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

def main():
    """Main function to generate the summary."""
    if len(sys.argv) > 3 or len(sys.argv) <2:
        print("Usage: python summary.py <input_json> [output_json]")
        sys.exit(1)
    if(len(sys.argv)==3):
        output_filepath = sys.argv[2]
    print("Working...")
    start_time = datetime.now()
    input_filepath = sys.argv[1]

    input_data = load_json(input_filepath)
    output_content = generate_summary(input_data)
    end_time = datetime.now()

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)
    date_time_str = end_time.isoformat()

    # Process output to handle potential paragraph structure
    output_lines = []
    for paragraph in output_content.split('\n\n'):
        # Add each paragraph as an item, or split further by lines if appropriate
        if len(paragraph.strip()) > 0:
            output_lines.append(paragraph.strip())

    # Get a UUID for this output
    output_uuid = str(uuid.uuid4())
    if (len(sys.argv) == 2):
        output_filepath = "output/summary/"+output_uuid+".json"
    else:
        output_filepath = sys.argv[3]

    output_data = {
        "uuid": output_uuid,
        "date_created": date_time_str,
        "task": "Summarise",
        "time_taken": time_taken_str,
        "output_text": output_lines
    }

    save_output(output_data, output_filepath)
    print(f"Generated Summary, output saved to {output_filepath}")

if __name__ == "__main__":
    main()