input_path = r"resources\chars.txt"
output_path = r"chars_fixed.txt"

new_lines = []
index = 0
last_base_index = None

with open(input_path, "r", encoding="utf-8") as infile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        char = parts[0]
        idx = parts[1]
        # Check for 'f' suffix
        if idx.endswith('f'):
            # Use the last base index with 'f'
            new_lines.append(f"{char} {last_base_index}f\n")
        else:
            # Assign new index and remember it
            new_lines.append(f"{char} {index}\n")
            last_base_index = index
            index += 1

with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(new_lines)

print(f"Re-indexed chars written to {output_path}")