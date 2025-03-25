# Usage note: use the model llama3.1:8b-instruct-q5_K_M for better results.
import json
import ollama
import sys
import uuid
from datetime import datetime
import re

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def merge_duplicate_facts(input_data):
    """Merge duplicate or similar facts from the input list"""
    prompt = "Merge the following duplicate or similar facts carefully. Avoid under-merging (keeping redundant facts) and over-merging (losing important details). Here are the facts:\n\n"
    for fact in input_data.get("facts", []):
        prompt += f"- {fact}\n"

    if "output_format" in input_data:
        prompt += f"\n\nProvide output as: {input_data['output_format']}"

    if "success_criteria" in input_data:
        criteria_str = json.dumps(input_data["success_criteria"], indent=2)
        prompt += f"\n\nSuccess Criteria:\n{criteria_str}"

    systemMsg = (
        "You are an AI assistant specialized in merging duplicate facts. "
        "Your goal is to combine facts that are identical or very similar, ensuring that unique details are preserved. "
        "Do not merge facts if slight differences contribute additional information. "
        "Provide a final list of unique, merged facts in a clear and concise manner. "
        "Each merged fact should be on its own line. Do not number the facts. "
        "Do not explain your reasoning. Do not add any conversational context. Do not output anything other than the merged facts."
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
    """Main function to merge duplicate facts."""
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python merge-duplicate-facts.py <input_json> [output_json]")
        sys.exit(1)
    if len(sys.argv) == 3:
        output_filepath = sys.argv[2]
    print("Working...")
    start_time = datetime.now()
    input_filepath = sys.argv[1]

    input_data = load_json(input_filepath)
    output_content = merge_duplicate_facts(input_data)
    end_time = datetime.now()

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)
    date_time_str = end_time.isoformat()

    # Process output to properly separate facts
    # First clean up any markdown formatting that might be present
    output_content = re.sub(r'^- ', '', output_content, flags=re.MULTILINE)
    output_content = re.sub(r'^[0-9]+\. ', '', output_content, flags=re.MULTILINE)

    # Split by newlines and filter out empty lines
    output_lines = [line.strip() for line in output_content.split('\n') if line.strip()]

    # Get a UUID for this output
    output_uuid = str(uuid.uuid4())
    if len(sys.argv) == 2:
        output_filepath = "output/merge-duplicate-facts/" + output_uuid + ".json"
    else:
        output_filepath = sys.argv[3]

    output_data = {
        "uuid": output_uuid,
        "date_created": date_time_str,
        "task": "Merge Duplicate Facts",
        "time_taken": time_taken_str,
        "merged_facts": output_lines
    }

    save_output(output_data, output_filepath)
    print(f"Merged Duplicate Facts, output saved to {output_filepath}")

if __name__ == "__main__":
    main()