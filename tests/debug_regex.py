import re
import os

def test_regex():
    file_path = r'd:\Drema Ai\data\C10ENG0FLIGHT0NCERT.txt'
    topic_num = "1"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"Read {len(content)} bytes from file.")
    
    # Regex from content_fetcher.py
    next_marker = rf'(?=UNIT\s*-\s*\d+|##\s*\d+\s*##|\Z)'
    pattern = rf'##\s*{re.escape(topic_num)}\s*##\s*(.*?){next_marker}'
    
    print(f"Testing pattern: {pattern}")
    
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        print("Match FOUND!")
        extracted = match.group(1).strip()
        print(f"Extracted length: {len(extracted)}")
        print(f"Start of extracted: {extracted[:100]}")
    else:
        print("Match NOT FOUND.")
        # Print first few lines of file to verify
        print("First 500 chars of file:")
        print(content[:500])

if __name__ == "__main__":
    test_regex()
