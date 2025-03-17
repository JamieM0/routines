import json
import ollama
import sys
import uuid
from datetime import datetime

def load_json(filepath):
    """Load JSON input file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_search_queries(input_data):
    """Generate search queries based on the input text."""
    prompt = f"""
    {" ".join(input_data.get("input_text", []))}
    Number of Search Queries to generate: {input_data["estimated_num_queries_to_generate"]}
    Output Format: {input_data["output_format"]}
    """

    if "success_criteria" in input_data:
        criteria_str = json.dumps(input_data["success_criteria"], indent=2)
        prompt += f"\n\nSuccess Criteria:\n{criteria_str}"

    systemMsg = ("You are a search query generation assistant. "
                 "Your task is to take a given topic and generate multiple high-quality search engine queries that help retrieve comprehensive, relevant, and useful information. "
                 "For each topic, generate a variety of queries, including: "
                 "General queries that provide a broad overview"
                 "Specific queries targeting authoritative sources"
                 "Question-based queries to find FAQ-style answers"
                 "Alternative phrasings to ensure diverse results"
                 "Advanced search operator queries (e.g., site:, filetype:, intitle:) for precision."
                 "Output the queries in a simple list format with no numbers, symbols, or extra formatting."
                 "Separate each query with a single newline.")

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
    """Main function to run the search query generation routine."""
    if len(sys.argv) > 3 or len(sys.argv) <2:
        print("Usage: python search-queries.py <input_json> [output_json]")
        sys.exit(1)
    if (len(sys.argv) == 3):
        output_filepath = sys.argv[2]

    print("Working...")
    start_time = datetime.now()  # Get the current datetime at the start
    input_filepath = sys.argv[1]

    input_data = load_json(input_filepath)
    output_content = generate_search_queries(input_data)
    end_time = datetime.now()  # Get the current datetime at the end

    time_taken = end_time - start_time
    time_taken_str = str(time_taken)

    date_time_str = end_time.isoformat()

    # Get a UUID for this output
    output_uuid = str(uuid.uuid4())

    if (len(sys.argv) == 2):
        output_filepath = "output/search-queries/"+output_uuid+".json"

    output_data = {
        "uuid": output_uuid,
        "date_created": date_time_str,
        "task": "Search Query Generations",
        "time_taken": time_taken_str,  # Store as string
        "search_queries": output_content.split("\n")
    }

    save_output(output_data, output_filepath)
    print(f"Generated Search Queries, output saved to {output_filepath}")

if __name__ == "__main__":
    main()