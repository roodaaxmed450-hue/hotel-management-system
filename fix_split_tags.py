import os
import re

def fix_split_tags(directory):
    # Match {{ ... }} or {% ... %} that span multiple lines
    split_pattern = re.compile(r'\{\{[^}]*?\n[^}]*?\}\}|\{%[^%]*?\n[^%]*?%\}', re.MULTILINE | re.DOTALL)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    def replacer(match):
                        tag = match.group(0)
                        # Remove newlines and redundant spaces inside the tag
                        # {% endif \n %} -> {% endif %}
                        # {{ \n booking }} -> {{ booking }}
                        fixed = re.sub(r'\s*\n\s*', ' ', tag)
                        return fixed
                    
                    new_content = split_pattern.sub(replacer, content)
                    
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8', newline='') as f:
                            f.write(new_content)
                        print(f"Fixed: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    fix_split_tags('hotel/templates/hotel')
