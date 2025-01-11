import sys

if len(sys.argv) < 2:
    print("Error: No file path provided.")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, 'r') as file:
        print(file.read())
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"Error reading file: {e}")