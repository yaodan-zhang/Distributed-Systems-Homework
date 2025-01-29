import sys
import os
import json
from collections import Counter

def main():
    # Ensure a command-line argument is provided
    if len(sys.argv) != 2:
        print("Usage: python map.py <i>")
        sys.exit(1)
    
    # Get the argument
    i = sys.argv[1]
    
    # Define input and output paths
    input_file = f"/titles/{i}.txt"
    output_file = f"/counts/{i}.json"
    flag_file = f"/counts/mapper_{i}_done"

    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Read the content of the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file '{input_file}': {e}")
        sys.exit(1)
    
    # Convert to lowercase and split into words
    words = text.lower().split()
    
    # Count word occurrences
    word_counts = Counter(words)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write word counts to the output file in JSON format
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(word_counts, f, indent=4)
        print(f"Word counts successfully written to '{output_file}'")
    except Exception as e:
        print(f"Error writing file '{output_file}': {e}")
        sys.exit(1)

    # Create the mapper completion flag file
    try:
        with open(flag_file, 'w', encoding='utf-8') as f:
            f.write("done")
        print(f"Mapper {i} completed. Flag file '{flag_file}' created.")
    except Exception as e:
        print(f"Error creating flag file '{flag_file}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
