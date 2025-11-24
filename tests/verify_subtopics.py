import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.components.content_fetcher import EducationContentFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_subtopic_extraction():
    fetcher = EducationContentFetcher(data_folder=r'd:\Drema Ai\data')
    
    # Test Case 1: Structured Chapter (Science Class 10, Chapter 8)
    print("\n--- Testing Structured Chapter (Science) ---")
    subtopics = fetcher.get_subtopics('CBSE', '10', 'Science', '8')
    print(f"Found {len(subtopics)} subtopics:")
    for s in subtopics[:5]: # Show first 5
        print(f"  {s['id']}: {s['name']}")
        
    if len(subtopics) > 1:
        print("PASS: Detected multiple subtopics for structured chapter.")
    else:
        print("FAIL: Did not detect multiple subtopics for structured chapter.")

    # Test Case 2: Unstructured Chapter (English Class 10, Chapter 1)
    print("\n--- Testing Unstructured Chapter (English) ---")
    subtopics_eng = fetcher.get_subtopics('CBSE', '10', 'English', '1')
    print(f"Found {len(subtopics_eng)} subtopics:")
    for s in subtopics_eng:
        print(f"  {s['id']}: {s['name']}")
        
    if len(subtopics_eng) >= 1:
        print("PASS: Handled unstructured chapter gracefully.")
    else:
        print("FAIL: Failed to handle unstructured chapter.")

    # Test Case 3: Content Filtering
    print("\n--- Testing Content Filtering ---")
    if len(subtopics) > 1:
        target_subtopic = subtopics[0]['id']
        print(f"Fetching content for subtopic: {target_subtopic}")
        result = fetcher.fetch_content('CBSE', '10', 'Science', '8', subtopics=[target_subtopic])
        
        if result['status'] == 'success':
            content = result['content']
            print(f"Content length: {len(content)}")
            print(f"Content preview: {content[:100]}...")
            
            if f"Subtopic {target_subtopic}" in content:
                 print("PASS: Content filtered and marked correctly.")
            else:
                 print("FAIL: Content filtering marker missing.")
        else:
            print(f"FAIL: Fetch content failed: {result['message']}")

if __name__ == "__main__":
    test_subtopic_extraction()
