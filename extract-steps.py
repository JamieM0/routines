import json
import ollama
import sys
from datetime import datetime


def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_step(input_data):
    """Extract steps based on the input text."""
    # Properly join the article text if it's a list
    if isinstance(input_data.get("article_text"), list):
        article_text = "\n\n".join(input_data.get("article_text"))
    else:
        article_text = input_data.get("article_text", "")

    # Create a clearer prompt with explicit instructions
    prompt = f"""Please extract the step-by-step instructions from the following article:

ARTICLE:
{article_text}

Remember to:
1. Extract only necessary, actionable steps
2. Keep steps concise and clear
3. Maintain logical order
4. Present steps in a simple list format without numbers or formatting

Each step should be on its own line, with no numbering.
"""

    systemMsg = ("You are an AI assistant specialized in extracting actionable instructions from text. "
                 "Your task is to take an article, recipe, or guide and distill it into a clear, step-by-step list of instructions. Follow these guidelines: "
                 "Extract only the necessary steps. Ignore background information, explanations, anecdotes, or unnecessary details. "
                 "Keep steps concise and clear. Ensure each step is actionable and uses direct language. "
                 "Maintain logical order. Ensure the steps follow a clear and natural progression. "
                 "Output the instructions in a simple list format with no numbers, symbols, markdown, or extra formatting. "
                 "Example Input: To make a great omelet, first, you need to gather your ingredients. People often wonder whether to use water or milk—chefs recommend milk. Crack the eggs into a bowl, whisk them, and add salt and pepper to taste. Then, heat a pan over medium heat and add butter. Once melted, pour in the eggs and let them sit before stirring. Cook until just set, then fold the omelet and serve immediately. "
                 "Example Output: \n"
                 "Crack eggs into a bowl and whisk.\n"
                 "Add salt, pepper, and a splash of milk.\n"
                 "Heat a pan over medium heat and add butter.\n"
                 "Pour in eggs and let them sit before stirring.\n"
                 "Cook until just set, then fold and serve.")

    response = ollama.chat(
        model=input_data["model"],
        messages=[{"role": "system", "content": systemMsg},
                  {"role": "user", "content": prompt}],
        options=input_data.get("parameters", {})
    )

    # Process the response to ensure it's in the right format
    content = response["message"]["content"]

    # Remove any markdown formatting that might be in the response
    content = content.replace('```', '').replace('**', '')

    # Filter out empty lines and lines that start with numbers
    lines = [line.strip() for line in content.split('\n')]
    steps = [line for line in lines if line and not (line.strip().startswith('1.') or
                                                     line.strip().startswith('2.') or
                                                     line.strip().startswith('3.') or
                                                     line.strip().startswith('Step') or
                                                     line.strip().startswith('**Step'))]

    # Return cleaned steps as a single string with line breaks
    return "\n".join(steps)


def save_output(output_data, output_filepath):
    """Save generated output to a JSON file."""
    with open(output_filepath, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)


def main():
    """Main function to run the search query generation routine."""
    if len(sys.argv) != 3:
        print("Usage: python extract-steps.py <input_json> <output_json>")
        sys.exit(1)

    print("Working...")
    start_time = datetime.now()  # Get the current datetime at the start
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    input_data = load_json(input_filepath)
    output_content = extract_step(input_data)
    end_time = datetime.now()  # Get the current datetime at the end

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)

    date_time_str = end_time.isoformat()

    # Split the output by newlines to get individual steps
    extracted_steps = [step for step in output_content.split("\n") if step.strip()]

    output_data = {
        "date_created": date_time_str,
        "task": "Step Extraction",
        "model_used": input_data["model"],
        "time_taken": time_taken_str,  # Store as string
        "article_text": input_data["article_text"],
        "extracted_steps": extracted_steps
    }

    save_output(output_data, output_filepath)
    print(f"Extracted Steps, output saved to {output_filepath}")


if __name__ == "__main__":
    main()