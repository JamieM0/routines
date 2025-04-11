import json
import sys
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args
)

def generate_automation_timeline(input_data):
    """Generate a historical timeline and future predictions for automation in a specific topic."""
    # Extract information from input data
    topic = input_data.get("topic", "")
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})
    
    # If input already contains timeline fields, use them directly
    if "timeline" in input_data:
        return input_data["timeline"]
    
    # Generate timeline using LLM
    systemMsg = (
        "You are an AI assistant specialized in creating historical timelines and future predictions "
        "for automation technologies. Your task is to create a comprehensive timeline that includes "
        "both historical events and future predictions related to the given topic."
    )
    
    user_msg = (
        f"Create an automation timeline for: {topic}\n\n"
        "Please provide:\n"
        "1. A historical timeline showing key developments by decade (1920s through present)\n"
        "2. Future predictions by decade showing how automation will likely progress\n"
        "3. Continue predictions until full automation is reached (if possible)\n\n"
        "Format your response as a JSON object with two main sections:\n"
        "- 'historical': an object with decades as keys (e.g., '1920s', '1930s') and descriptions as values\n"
        "- 'predictions': an object with future decades as keys (e.g., '2030s', '2040s')\n"
        "Only include decades that have significant events relevant to the topic."
    )
    
    # Use chat_with_llm to generate timeline
    response = chat_with_llm(model, systemMsg, user_msg, parameters)
    
    try:
        # Try to parse JSON response
        timeline = parse_llm_json_response(response)
        return timeline
    except json.JSONDecodeError:
        print("Error: LLM response is not valid JSON. Full response: " + response)
        return None

def main():
    """Main function to run the timeline generation."""
    usage_msg = "Usage: python generate_automation_timeline.py <input_json> [output_json]"
    input_filepath, specified_output_filepath = handle_command_args(usage_msg)

    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    timeline = generate_automation_timeline(input_data)
    
    if timeline is None:
        print("Failed to generate automation timeline.")
        sys.exit(1)
    
    # Get output filepath and UUID
    output_filepath, output_uuid = get_output_filepath(
        "automation-timeline", 
        specified_path=specified_output_filepath
    )
    
    # Create process metadata
    process_metadata = create_output_metadata("Automation Timeline Generation", start_time, output_uuid)
    
    # Combine process metadata with output content
    output_data = {
        **process_metadata,
        "timeline": timeline
    }

    save_output(output_data, output_filepath)
    print(f"Generated automation timeline, output saved to {output_filepath}")

if __name__ == "__main__":
    main()
