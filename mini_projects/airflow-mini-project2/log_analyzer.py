import sys
from pathlib import Path

def analyze_file(file_path):
    error_count = 0
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            if "ERROR" in line:
                error_count += 1
                messages.append(line.strip())
    return error_count, messages

if len(sys.argv) != 2:
    print("Usage: python log_analyzer.py <log_directory>")
    sys.exit(1)

log_dir = Path(sys.argv[1])
log_files = log_dir.rglob("*.log")

total_errors = 0
all_messages = []

for log_file in log_files:
    count, messages = analyze_file(log_file)
    total_errors += count
    all_messages.extend(messages)

print(f"Total number of errors: {total_errors}")
print("Here are all the errors:")
for msg in all_messages:
    print(msg)
