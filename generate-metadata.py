import json
import sys
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm,
    create_output_metadata, get_output_filepath, handle_command_args
)

def generate_page_metadata(input_data):
    """Generate standardized metadata for a topic page."""
    # Extract information from input data
    topic = input_data.get("topic", "")
    model = input_data.get("model", "gemma3")
    parameters = input_data.get("parameters", {})
    
    # If input already contains metadata fields, use them directly
    if "metadata" in input_data:
        return input_data["metadata"]
    
    # Otherwise, generate metadata using LLM
    systemMsg = (
        "You are an AI assistant specialized in creating consistent metadata for technical topics. "
        "Generate appropriate metadata for the topic provided, including: "
        "- A descriptive title (using the topic name) MAXIMUM 2-3 WORDS DO NOT INCLDUE A SUBTITLE (e.g., ANYTHING AFTER A SEMICOLON) "
        "- A subtitle that explains the scope "
        "- Current automation status (No Automation, Very Early Automation, Early Automation, Some Automation, Partially Fully Automated, Mostly Fully Automated, or Fully Automated) "
        "- Percentage estimate of progress toward full automation (as a percentage). BE CRITICAL, do not exaggerate current status. E.g., '25%' would be appropriate for topics where some partial automation is POSSIBLE."
        "- Explanatory text (2-3 FULL paragraphs) that describes the topic and its automation journey."
        "Format your response as a JSON object with these fields."
    )
    
    user_msg = f"Create metadata for a Universal Automation Wiki page about: {topic}"
    
    # Use chat_with_llm to generate metadata
    response = chat_with_llm(model, systemMsg, user_msg, parameters)
    
    try:
        # Try to parse JSON response directly
        metadata = json.loads(response)
        return metadata
    except json.JSONDecodeError:
        # Check if response contains code fence markers
        if "```json" in response:
            try:
                # Extract content between code fence markers
                json_content = response.split("```json", 1)[1].split("```", 1)[0].strip()
                metadata = json.loads(json_content)
                return metadata
            except (json.JSONDecodeError, IndexError) as e:
                print(f"Error extracting JSON from code block: {str(e)}")
        
        # Alternative approach - try to find JSON-like content
        try:
            # Look for content between curly braces
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                potential_json = response[start:end]
                metadata = json.loads(potential_json)
                return metadata
        except json.JSONDecodeError:
            pass
            
        print("Error: LLM response is not valid JSON. Full response: " + response)
        return None

def main():
    """Main function to run the metadata generation."""
    usage_msg = "Usage: python generate-metadata.py <input_json> [output_json]"
    input_filepath, specified_output_filepath = handle_command_args(usage_msg)

    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    metadata = generate_page_metadata(input_data)
    
    if metadata is None:
        print("Failed to generate metadata.")
        sys.exit(1)
    
    # Get output filepath and UUID
    output_filepath, output_uuid = get_output_filepath(
        "metadata", 
        specified_path=specified_output_filepath
    )
    
    # Create process metadata
    process_metadata = create_output_metadata("Page Metadata Generation", start_time, output_uuid)
    
    # Combine process metadata with output content
    output_data = {
        **process_metadata,
        "page_metadata": metadata
    }

    save_output(output_data, output_filepath)
    print(f"Generated page metadata, output saved to {output_filepath}")

if __name__ == "__main__":
    main()
