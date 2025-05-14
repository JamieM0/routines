import json
import sys
from datetime import datetime
from utils import (
    load_json, save_output, chat_with_llm, parse_llm_json_response,
    create_output_metadata, get_output_filepath, handle_command_args,
    saveToFile
)

flowUUID = None # Global variable for flow UUID

def generate_page_metadata(input_data, save_inputs=False):
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
        "Generate appropriate metadata for the topic provided, including:\n"
        "- A descriptive title (using the topic name) MAXIMUM 2-3 WORDS DO NOT INCLUDE A SUBTITLE "
        "  (e.g., ANYTHING AFTER A SEMICOLON)\n"
        "- A subtitle that explains the scope\n"
        "- Current automation status. Choose one of the following by reviewing the automation status guidelines:\n"
        "    No Automation/Manual\n"
        "    Tool Supported\n"
        "    Support Automation\n"
        "    Scripted Automation\n"
        "    Coordinated Automation\n"
        "    Self-Managing Automation\n"
        "    Fully Autonomous (Self-Evolving)\n"
        "- Percentage estimate of progress toward full automation (as a percentage). BE CRITICAL, do not exaggerate current status. "
        "E.g., '25%' would be appropriate for topics where some partial automation is POSSIBLE.\n"
        "- Explanatory text (2-3 FULL paragraphs) that describes the topic and its automation journey.\n"
        "Format your response as a JSON object with these fields.\n\n"

        "Automation Status Definitions:\n\n"

        "1. No Automation/Manual\n"
        "Definition: Tasks are performed entirely by humans without the aid of any automated tools or systems. "
        "Every action, decision, and step relies solely on human intervention and physical or cognitive effort. "
        "The process is fundamentally manual from initiation to completion.\n"
        "Key Criteria:\n"
        "    - Human Initiative: Every step requires direct human initiation and execution.\n"
        "    - Basic Tooling: Only non-automated, basic instruments (e.g., hand tools, simple measuring devices).\n"
        "    - No Digital Assistance: Absence of software, scripts, or digital interfaces to guide or perform actions.\n"
        "    - Direct Sensory Feedback: Reliance on human senses for monitoring and control.\n"
        "Examples:\n"
        "    * Manually calculating inventory levels using pen and paper.\n"
        "    * Hand-drafting architectural blueprints.\n"
        "    * Assembling a product using only hand tools without power assistance.\n"
        "    * Sorting physical mail by hand based on destination addresses.\n\n"

        "2. Tool Supported\n"
        "Definition: Humans operate specialized tools, equipment, or GUIs that simplify or enhance manual tasks but do not execute them automatically. "
        "These tools require continuous human input and control for each step.\n"
        "Key Criteria:\n"
        "    - Tool-Enhanced Manual Work: Technology aids human operators but doesn't replace direct involvement.\n"
        "    - Step-by-Step Human Control: Each action requires explicit human command via the tool.\n"
        "    - No Automated Logic: Tools lack independent decision-making or sequence execution.\n"
        "    - Efficiency Gain: Tools primarily offer speed, precision, or ease-of-use improvements.\n"
        "Examples:\n"
        "    * Using a calculator for complex arithmetic instead of manual calculation.\n"
        "    * Employing a word processor for document creation instead of handwriting.\n"
        "    * Using a power drill instead of a manual screwdriver for assembly.\n"
        "    * Utilizing a GUI-based configuration tool requiring manual input for each setting.\n\n"

        "3. Support Automation\n"
        "Definition: Systems provide context-aware suggestions, checklists, validation, or prompts to guide human operators. "
        "Humans retain authority to approve and execute actions; the system offers partial decision support.\n"
        "Key Criteria:\n"
        "    - Contextual Guidance: System provides relevant info or recommendations.\n"
        "    - Human Approval Required: Suggestions or plans must be confirmed by a human.\n"
        "    - Partial Decision Support: The system assists in decision-making but doesn't choose autonomously.\n"
        "    - Validation & Error Checking: Tools may automatically check for input errors.\n"
        "Examples:\n"
        "    * Software offering spell-check and grammar suggestions as a user types.\n"
        "    * An installation wizard guiding a user through setup steps with defaults and validation.\n"
        "    * A diagnostic system suggesting potential fault causes, requiring human verification.\n"
        "    * An IDE providing code completion suggestions and syntax highlighting.\n\n"

        "4. Scripted Automation\n"
        "Definition: Predefined scripts, macros, or batch processes execute a specific, repeatable sequence of tasks with minimal human intervention beyond initiation.\n"
        "Key Criteria:\n"
        "    - Predefined Sequences: Automation follows a fixed, coded set of instructions.\n"
        "    - Minimal Intervention (Post-Initiation): Once started, the script runs to completion.\n"
        "    - Repeatability: Designed for tasks frequently performed the same way.\n"
        "    - Limited Adaptability: Scripts require manual updates to handle changes.\n"
        "    - Requires Maintenance: Scripts need ongoing upkeep as underlying systems change.\n"
        "Examples:\n"
        "    * A script that automatically backs up specific directories on schedule.\n"
        "    * A spreadsheet macro formatting data and generating a report.\n"
        "    * Automated test scripts executing predefined test cases.\n"
        "    * A batch job processing daily transaction logs overnight.\n\n"

        "5. Coordinated Automation\n"
        "Definition: Multiple automated tools, scripts, and systems are coordinated through workflows managed by a central orchestrator (e.g., CI/CD pipeline, BPM). "
        "Human intervention is limited to exceptions or complex decisions.\n"
        "Key Criteria:\n"
        "    - Workflow Coordination: A central system manages sequence, timing, and data flow.\n"
        "    - API Integration: Tools and systems communicate via APIs.\n"
        "    - Conditional Logic: Workflows include branching, loops, and conditional execution.\n"
        "    - Exception Handling: Predefined procedures for human-handled errors.\n"
        "    - State Management: The orchestrator tracks end-to-end process state.\n"
        "Examples:\n"
        "    * A CI/CD pipeline building, testing, and deploying software.\n"
        "    * An order-fulfillment system coordinating inventory, payment, packaging, and shipping.\n"
        "    * A security orchestration platform responding to alerts and creating incident tickets.\n"
        "    * BPM software automating employee onboarding across HR, IT, and facilities.\n\n"

        "6. Self-Managing Automation\n"
        "Definition: Systems monitor their own state, adapt to conditions, and optimize performance based on policies or goals without direct human commands.\n"
        "Key Criteria:\n"
        "    - Self-Configuration: Systems configure themselves per high-level policies.\n"
        "    - Self-Healing: Detect failures and take corrective actions automatically.\n"
        "    - Self-Optimization: Continuously adjust parameters for performance or efficiency.\n"
        "    - Self-Protection: Defend against intrusions or failures automatically.\n"
        "    - Policy-Driven: Governed by rules and objectives rather than step-by-step instructions.\n"
        "    - Minimal Human Oversight: Humans set policies and monitor health.\n"
        "Examples:\n"
        "    * Cloud platforms auto-scaling resources based on traffic.\n"
        "    * Adaptive databases optimizing query plans.\n"
        "    * Network infrastructure rerouting traffic to avoid congestion.\n"
        "    * Climate control systems adjusting conditions based on sensors.\n\n"

        "7. Fully Autonomous (Self-Evolving)\n"
        "Definition: End-to-end processes operate and adapt continuously without human involvement, using ML/AI to improve over time.\n"
        "Key Criteria:\n"
        "    - Zero Human Triggers: Operates independently, initiating tasks on its own.\n"
        "    - Continuous Learning & Adaptation: Improves strategies based on data and feedback.\n"
        "    - Self-Governing: Makes high-level strategic decisions within its domain.\n"
        "    - High Complexity Handling: Manages complex, dynamic, unpredictable environments.\n"
        "    - Transparency & Auditability: Provides clear logs and explanations for actions.\n"
        "Examples:\n"
        "    * A global supply chain that learns from market trends and disruptions.\n"
        "    * An AI-driven portfolio manager adjusting holdings continuously.\n"
        "    * Research platforms designing, executing, and analyzing experiments autonomously.\n"
        "    * A self-balancing power grid optimizing generation and consumption.\n"
    )
    
    user_msg = f"Create metadata for a Universal Automation Wiki page about: {topic}"
    
    # Save inputs to file if requested
    if save_inputs:
        save_path = f"flow/{flowUUID}/inputs/1-in.json"
        saveToFile(systemMsg, user_msg, save_path)
    
    # Use chat_with_llm to generate metadata
    response = chat_with_llm(model, systemMsg, user_msg, parameters)
    # Parse JSON using shared utility to extract JSON block reliably
    metadata = parse_llm_json_response(response)
    if not isinstance(metadata, dict):
        print("Error: Parsed metadata is not a JSON object. Full response: " + response)
        return None
    return metadata

def main():
    """Main function to run the metadata generation."""
    global flowUUID
    usage_msg = "Usage: python generate-metadata.py <input_json> [output_json] [-saveInputs] [-uuid=\"UUID\"] [-flow_uuid=\"FLOW-UUID\"]"
    input_filepath, specified_output_filepath, save_inputs, custom_uuid, flow_uuid_arg = handle_command_args(usage_msg)
    flowUUID = flow_uuid_arg # Set the global variable

    print("Working...")
    start_time = datetime.now()
    
    input_data = load_json(input_filepath)
    metadata = generate_page_metadata(input_data, save_inputs)
    
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
