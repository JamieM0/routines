import json
import ollama
import sys
from datetime import datetime


def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_facts(input_data):
    """Generate a list of facts using an LLM based on input JSON parameters."""
    # Define general system prompt within the code
    systemMsg = (
        "You are a knowledgeable assistant specialized in providing accurate, concise, and informative facts about various topics. "
        "Your responses should be factual, specific, and organized. "
        "When asked about a subject, provide clear, detailed information based on your knowledge, focusing on relevant details. "
        "Present your information in a clear, structured format with one fact per line. "
        "Avoid unnecessary commentary, opinions, or irrelevant details. "
        "Focus on providing factual, educational content about the requested topic."
        "Focus on having a wide variety of facts."
        "Output the instructions in a simple list format with no numbers, symbols, markdown, or extra formatting. ")

    response = ollama.chat(
        model=input_data["model"],
        messages=[
            {"role": "system", "content": systemMsg},
            {"role": "user", "content": input_data["task"]}
        ],
        options=input_data.get("parameters", {})
    )

    return response["message"]["content"]


def save_output(output_data, output_filepath):
    """Save generated output to a JSON file."""
    with open(output_filepath, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)


def main():
    """Main function to run the fact generation routine."""
    if len(sys.argv) != 3:
        print("Usage: python prompt.py <input_json> <output_json>")
        sys.exit(1)

    print("Working...")
    start_time = datetime.now()  # Get the current datetime at the start
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    input_data = load_json(input_filepath)
    output_content = generate_facts(input_data)
    end_time = datetime.now()  # Get the current datetime at the end

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)

    date_time_str = end_time.isoformat()

    # Process the output content - split by new lines and clean up
    facts_list = [fact.strip() for fact in output_content.split("\n") if fact.strip()]

    output_data = {
        "date_created": date_time_str,
        "model_used": input_data["model"],
        "time_taken": time_taken_str,  # Store as string
        "task": input_data["task"],
        "facts": facts_list
    }

    save_output(output_data, output_filepath)
    print(f"Generated facts, saved to {output_filepath}")


if __name__ == "__main__":
    main()