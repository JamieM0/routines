import json
import ollama
import sys
from datetime import datetime

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def translate_basic_english(input_data):
    """Convert the input text to BASIC English."""
    prompt = f"""
    {" ".join(input_data.get("input_text", []))}
    Output Format: {input_data["output_format"]}
    """

    systemMsg = ("Convert the given text into BASIC English. "
                 "Use only words from the BASIC English list (850 words). "
                 "Make all sentences short, clear, and simple. Do not use difficult words. "
                 "If needed, explain with easy words. Keep numbers and measurements clear. "
                 "If the sentence is already simple, do not change it.")

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
    """Main function to run the BASIC English convert routine."""
    if len(sys.argv) != 3:
        print("Usage: python basic-english.py <input_json> <output_json>")
        sys.exit(1)

    print("Working...")
    start_time = datetime.now()  # Get the current datetime at the start
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    input_data = load_json(input_filepath)
    output_content = translate_basic_english(input_data)
    end_time = datetime.now()  # Get the current datetime at the end

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)

    date_time_str = end_time.isoformat()

    output_data = {
        "date_created": date_time_str,
        "task": "BASIC English conversion",
        "model_used": input_data["model"],
        "time_taken": time_taken_str,  # Store as string
        "input_text": input_data["input_text"],
        "output_text": output_content.split("\n")
    }

    save_output(output_data, output_filepath)
    print(f"Generated BASIC English, output saved to {output_filepath}")

if __name__ == "__main__":
    main()