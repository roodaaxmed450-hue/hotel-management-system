import os
import re

def find_split_tags(directory):
    split_pattern = re.compile(r'\{\{[^}]*\n[^}]*\}\}|\{%[^%]*\n[^%]*%\}', re.MULTILINE)
    with open('split_tags_report.txt', 'w', encoding='utf-8') as report:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = split_pattern.finditer(content)
                        for match in matches:
                            line_no = content.count('\n', 0, match.start()) + 1
                            report.write(f"File: {path}, Line: {line_no}\n")
                            report.write(f"Content:\n{match.group()}\n")
                            report.write("-" * 20 + "\n")

if __name__ == "__main__":
    find_split_tags('hotel/templates/hotel')
