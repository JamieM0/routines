import json
import sys
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args
)


def generate_automation_challenges(input_data):
    """Generate a list of challenges for automation in a specific topic."""
    # Extract information from input data
    topic = input_data.get("topic", "")
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})

    # Generate a list of challenges using LLM
    systemMsg = (
        "You are an AI assistant specialized in analyzing automation challenges. "
        "Your task is to identify and explain the current technical, practical, and "
        "conceptual challenges that make automation difficult in a specific field or topic."
    )

    user_msg = (
        f"Create a list of automation challenges for: {topic}\n\n"
        "Please provide:\n"
        "1. 4-8 specific challenges that make automation difficult in this field\n"
        "2. For each challenge, provide a concise title and detailed explanation\n"
        "3. Focus on technical limitations, practical constraints, and human expertise that's difficult to replicate\n\n"
        "Format your response as a JSON object.\n"
        "Only include challenges that are significantly relevant to the topic."
    )

    # Use chat_with_llm to generate a list of challenges
    response = chat_with_llm(model, systemMsg, user_msg, parameters)

    try:
        # Try to parse JSON response
        challenges = parse_llm_json_response(response)
        return challenges
    except json.JSONDecodeError:
        print("Error: LLM response is not valid JSON. Full response: " + response)
        return None


def main():
    """Main function to run the challenge generation function."""
    usage_msg = "Usage: python generate_automation_challenges.py <input_json> [output_json]"
    input_filepath, specified_output_filepath = handle_command_args(usage_msg)

    print("Working...")
    start_time = datetime.now()

    input_data = load_json(input_filepath)
    challenges = generate_automation_challenges(input_data)

    if challenges is None:
        print("Failed to generate automation challenges.")
        sys.exit(1)

    # Get output filepath and UUID
    output_filepath, output_uuid = get_output_filepath(
        "automation-challenges",
        specified_path=specified_output_filepath
    )

    # Create process metadata
    process_metadata = create_output_metadata("Automation Challenges Generation", start_time, output_uuid)

    # Combine process metadata with output content
    output_data = {
        **process_metadata,
        "challenges": challenges
    }

    save_output(output_data, output_filepath)
    print(f"Generated automation challenges, output saved to {output_filepath}")


if __name__ == "__main__":
    main()
