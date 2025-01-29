import os
import json
from collections import Counter

def main():
    # Define file paths and parameters
    mapper_done_flags = [f"counts/mapper_{i}_done" for i in range(1, 10)]
    input_files = [f"counts/{i}.json" for i in range(1, 10)]
    output_file = "counts/total_counts.json"

    # Wait until all mapper done flags exist
    print("Waiting for all mappers to finish...")
    while not all(os.path.exists(flag) for flag in mapper_done_flags):
        pass  # Keep waiting until all mappers are done

    print("All mappers are done. Combining word counts...")

    # Combine word counts from all mapper outputs
    combined_counts = Counter()
    for input_file in input_files:
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    word_counts = json.load(f)
                    combined_counts.update(word_counts)
            except Exception as e:
                print(f"Error reading file '{input_file}': {e}")
    
    # Sort combined counts by total count (descending) and write to output file
    sorted_counts = dict(sorted(combined_counts.items(), key=lambda item: item[1], reverse=True))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_counts, f, indent=4)
        print(f"Combined word counts successfully written to '{output_file}'")
    except Exception as e:
        print(f"Error writing file '{output_file}': {e}")
        return

    # Optional: Clean up the mapper done flags
    for flag in mapper_done_flags:
        os.remove(flag)

if __name__ == "__main__":
    main()
