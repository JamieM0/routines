import json
import ollama
import sys
from datetime import datetime


def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def translate_simplified_technical_english(input_data):
    """Convert the input text to simplified technical english (STE)."""
    prompt = f"Convert this text to Simplified Technical English:\n\n{input_data.get("input_text")}"

    if "output_format" in input_data:
        prompt += f"\n\nProvide output as: {input_data['output_format']}"

    systemMsg = ("You are an AI assistant specializing in Simplified Technical English (STE) conversion. "
                 "Follow these strict STE rules:"
                 "\n1. USE SHORT SENTENCES - Maximum 20 words per sentence. Prefer 10-15 words."
                 "\n2. ONE IDEA PER SENTENCE - Split complex sentences into multiple simple ones."
                 "\n3. USE ACTIVE VOICE ONLY - Eliminate all passive voice constructions."
                 "\n4. USE SIMPLE VOCABULARY - Replace complex words with simpler alternatives."
                 "\n5. BE CONSISTENT - Use the same term for the same concept throughout."
                 "\n6. USE APPROVED TECHNICAL TERMS ONLY - Avoid jargon and unnecessary technical terms."
                 "\n7. REMOVE AMBIGUITY - Each sentence must have only one possible interpretation."
                 "\n8. USE LISTS FOR SEQUENTIAL INSTRUCTIONS - Number steps clearly when applicable."
                 "\n9. ELIMINATE UNNECESSARY WORDS - Remove all words that don't add essential meaning."
                 "\n10. AVOID COMPLEX VERB TENSES - Use simple present or simple past whenever possible."
                 "\nExample input: The implementation of the methodology necessitates a comprehensive understanding of underlying principles, which may appear convoluted to novice practitioners."
                 "\nExample output: This method requires you to understand basic principles. These principles may seem complex to new users.")

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
    """Main function to run the Simplified Technical English conversion."""
    if len(sys.argv) != 3:
        print("Usage: python simplified-technical-english.py <input_json> <output_json>")
        sys.exit(1)

    print("Working...")
    start_time = datetime.now()
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    input_data = load_json(input_filepath)
    output_content = translate_simplified_technical_english(input_data)
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

    output_data = {
        "date_created": date_time_str,
        "task": "Simplified Technical English conversion",
        "model_used": input_data["model"],
        "time_taken": time_taken_str,
        "input_text": input_data.get("input_text", input_data.get("task", "")),
        "output_text": output_lines
    }

    save_output(output_data, output_filepath)
    print(f"Generated Simplified Technical English, output saved to {output_filepath}")


if __name__ == "__main__":
    main()