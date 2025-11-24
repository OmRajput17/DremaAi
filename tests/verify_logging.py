import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.components.content_fetcher import EducationContentFetcher
from src.logging import get_logger

# Setup logging to stdout to see it in the output
logging.basicConfig(level=logging.INFO)

def test_logging():
    fetcher = EducationContentFetcher()
    
    # Test with a known topic (e.g., Science Class 10 Chapter 8)
    # Print available subjects for debugging
    print(f"Available subjects for Class 10: {fetcher.get_subjects('CBSE', '10')}")

    print("Fetching content...")
    result = fetcher.fetch_content(
        board="CBSE", 
        class_num="10", 
        subject="Science", 
        topic_num="8",
        subtopics=["8.1"]
    )
    
    print("\n--- Result Status ---")
    print(result['status'])
    if result['status'] == 'error':
        print(result['message'])

if __name__ == "__main__":
    test_logging()
