import os
import sys
import uuid
import json
import subprocess
from datetime import datetime
from utils import (
    load_json, save_output, create_output_metadata,
    get_output_filepath, handle_command_args
)

def run_program(program_name, input_path, output_path, extra_args=None):
    """Run a program with the specified input and output paths."""
    print(f"Running {program_name}...")
    
    # Build command with any extra arguments
    command = [sys.executable, program_name, input_path, output_path]
    if extra_args:
        command.extend(extra_args)
        
    try:
        # Run the program and capture its output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  {program_name} completed successfully")
        print(f"  {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR running {program_name}: {e}")
        print(f"  STDOUT: {e.stdout}")
        print(f"  STDERR: {e.stderr}")
        return False

def main():
    """Main function to run the flow of programs."""
    usage_msg = "Usage: python flow-maker.py <input_json> [breadcrumbs]"
    
    if len(sys.argv) < 2:
        print(usage_msg)
        sys.exit(1)
        
    input_filepath = sys.argv[1]
    
    # Get breadcrumbs if provided, otherwise use a default empty value
    breadcrumbs = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print("Starting flow process...")
    start_time = datetime.now()
    
    # Load the input data
    input_data = load_json(input_filepath)
    
    # Generate a UUID for this flow
    flow_uuid = str(uuid.uuid4())
    print(f"Flow UUID: {flow_uuid}")
    
    # Create flow directory
    flow_dir = os.path.join("flow", flow_uuid)
    os.makedirs(flow_dir, exist_ok=True)
    
    # Save a copy of the input file in the flow directory
    input_copy_path = os.path.join(flow_dir, "input.json")
    with open(input_copy_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=4)
    
    # Save breadcrumbs to a file in the flow directory
    if breadcrumbs:
        breadcrumbs_path = os.path.join(flow_dir, "breadcrumbs.txt")
        with open(breadcrumbs_path, "w", encoding="utf-8") as f:
            f.write(breadcrumbs)
        print(f"Breadcrumbs saved: {breadcrumbs}")
    
    # Define the programs to run in order
    programs = [
        ("generate-metadata.py", "1.json"),  # 1. metadata.py
        ("hallucinate-tree.py", "2.json"),   # 2. hallucinate-tree.py
        ("generate-automation-timeline.py", "3.json"),  # 3. generate-automation-timeline.py
        ("generate-automation-challenges.py", "4.json"), # 4. generate-automation-challenges.py
        ("automation-adoption.py", "5.json"),  # 5. automation-adoption.py
        ("current-implementations.py", "6.json"),  # 6. current-implementations.py
        ("return-analysis.py", "7.json"),  # 7. return-analysis.py
        ("future-technology.py", "8.json"),  # 8. future-technology.py
        ("specifications-industrial.py", "9.json"),  # 9. specifications-industrial.py
    ]
    
    # Run each program in sequence
    for i, (program, output_filename) in enumerate(programs):
        print(f"\nStep {i+1}/{len(programs)}: Running {program}")
        
        # Define output path for this program
        output_path = os.path.join(flow_dir, output_filename)
        
        # Handle special parameters for hallucinate-tree.py
        extra_args = None
        if program == "hallucinate-tree.py":
            extra_args = ["-flat"]
        
        # Run the program
        success = run_program(program, input_copy_path, output_path, extra_args)
        
        if not success:
            print(f"Warning: {program} failed to complete successfully")
    
    # Create flow metadata
    end_time = datetime.now()
    time_taken = end_time - start_time
    
    flow_metadata = {
        "uuid": flow_uuid,
        "date_created": end_time.isoformat(),
        "task": "Complete Automation Flow",
        "time_taken": str(time_taken),
        "input_file": input_filepath,
        "programs_run": [p[0] for p in programs]
    }
    
    # Save flow metadata
    metadata_path = os.path.join(flow_dir, "flow-metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(flow_metadata, f, indent=4)
    
    # Now run assemble.py to generate the HTML output
    print("\nGenerating HTML output using assemble.py...")
    
    # Determine the output filename based on breadcrumbs if available
    output_filename = "output.html"
    if breadcrumbs:
        # Extract the last part of the breadcrumbs to use as the filename
        page_name = breadcrumbs.split('/')[-1]
        output_filename = f"{page_name}.html"
    
    html_output_path = os.path.join(flow_dir, output_filename)
    
    # Add breadcrumbs_path as an additional argument to assemble.py if available
    extra_args = []
    if breadcrumbs:
        extra_args = [breadcrumbs]
        
    assemble_success = run_program("assemble.py", flow_dir, html_output_path, extra_args)
    
    if assemble_success:
        print(f"HTML output generated successfully at: {os.path.abspath(html_output_path)}")
    else:
        print("Warning: HTML generation failed")
    
    print(f"\nFlow process completed in {time_taken}")
    print(f"Output files saved to: {os.path.abspath(flow_dir)}")

if __name__ == "__main__":
    main()