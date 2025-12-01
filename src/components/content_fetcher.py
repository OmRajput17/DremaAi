"""
Content Fetcher Component
Handles fetching educational content from data files
"""
import os
import json
import re
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class EducationContentFetcher:
    """Fetches educational content based on board, class, subject, and topic."""
    
    def __init__(self, category_file='category.json', topics_file='topics.json', data_folder='data'):
        """
        Initialize the content fetcher with JSON files and data folder.
        
        File Structures:
        - category.json: Boards -> [BoardName] -> Classes -> [ClassNum] -> Subjects -> [SubjectName] -> Books
        - topics.json: [BoardName] -> [ClassNum] -> [SubjectName] -> {topic_num: topic_name}
        """
        logger.info("Initializing EducationContentFetcher...")
        self.data_folder = data_folder
        
        # Load JSON files
        logger.debug(f"Loading category file: {category_file}")
        with open(category_file, 'r', encoding='utf-8') as f:
            self.category_data = json.load(f)
        
        logger.debug(f"Loading topics file: {topics_file}")
        with open(topics_file, 'r', encoding='utf-8') as f:
            self.topics_data = json.load(f)
        
        logger.info("EducationContentFetcher initialized successfully")
    
    def get_boards(self):
        """Get list of available boards."""
        return list(self.category_data.get('Boards', {}).keys())
    
    def get_classes(self, board):
        """Get list of available classes for a board."""
        return list(self.category_data['Boards'].get(board, {}).get('Classes', {}).keys())
    
    def get_subjects(self, board, class_num):
        """Get list of available subjects for a board and class."""
        return list(self.category_data['Boards'].get(board, {})
                   .get('Classes', {}).get(str(class_num), {})
                   .get('Subjects', {}).keys())
    
    def get_topics(self, board, class_num, subject):
        """Get list of available topics for a board, class, and subject."""
        # topics.json structure: board -> class_num -> subject -> {topic_num: topic_name}
        topics = self.topics_data.get(board, {}).get(str(class_num), {}).get(subject, {})
        logger.debug(f"Retrieved topics for {board}/{class_num}/{subject}: {len(topics)} topics found")
        return {num: name for num, name in topics.items()}
    
    def get_books(self, board, class_num, subject):
        """Get list of books for a board, class, and subject."""
        books = self.category_data['Boards'].get(board, {}).get('Classes', {}).get(str(class_num), {}).get('Subjects', {}).get(subject, {}).get('Books', {})
        return list(books.values())
    
    def extract_topic_from_book(self, book_content, topic_num):
        """
        Extract topic ONLY when chapter is marked as:
            1. ##x##
            2. UNIT-x / Unit-x / unit-x  (dash required)
        """
        topic_num = str(topic_num).strip()

        # Stop when next UNIT-x or ##x##
        next_marker = rf'(?=UNIT\s*-\s*\d+|##\s*\d+\s*##|\Z)'

        patterns = [
            # Pattern 1: ##x##
            rf'##\s*{re.escape(topic_num)}\s*##\s*(.*?){next_marker}',
            # Pattern 2: UNIT-x (dash required)
            rf'UNIT\s*-\s*{re.escape(topic_num)}\s*(.*?){next_marker}',
        ]

        flags = re.IGNORECASE | re.DOTALL

        for pat in patterns:
            match = re.search(pat, book_content, flags)
            if match:
                return match.group(1).strip()

        return None
    
    def fetch_content(self, board, class_num, subject, topic_num):
        """
        Fetch the topic content from the appropriate book.
        
        Returns:
            dict: Contains 'book_name', 'book_id', 'topic_name', 'content', and 'status'
        """
        logger.info(f"Fetching content for: Board={board}, Class={class_num}, Subject={subject}, Topic={topic_num}")
        
        result = {
            'board': board,
            'class': class_num,
            'subject': subject,
            'topic_num': topic_num,
            'book_name': None,
            'book_id': None,
            'topic_name': None,
            'content': None,
            'status': 'error',
            'message': ''
        }
        
        # Get topic name (optional - may not be in topics.json)
        topics = self.get_topics(board, class_num, subject)
        if topics and str(topic_num) in topics:
            result['topic_name'] = topics[str(topic_num)]
            logger.debug(f"Topic name found: {result['topic_name']}")
        else:
            result['topic_name'] = f"Topic {topic_num}"
            logger.debug(f"Topic name not found in topics.json, using default: {result['topic_name']}")
        
        # Get books for this subject
        books = self.get_books(board, class_num, subject)
        if not books:
            result['message'] = "No books found for this subject in category.json"
            logger.warning(result['message'])
            return result
        
        logger.info(f"Searching in {len(books)} book(s)...")
        
        # Try each book until we find the topic
        books_checked = []
        for book in books:
            book_id = book.get('book_id')
            book_name = book.get('Name')
            book_path = os.path.join(self.data_folder, f"{book_id}.txt")
            
            books_checked.append(book_id)
            logger.debug(f"Checking book: {book_name} (ID: {book_id})")
            
            if not os.path.exists(book_path):
                logger.debug(f"Book file not found: {book_path}")
                continue
            
            try:
                with open(book_path, 'r', encoding='utf-8') as f:
                    book_content = f.read()
                
                # Extract the specific topic
                topic_content = self.extract_topic_from_book(book_content, topic_num)
                
                if topic_content:
                    result['book_name'] = book_name
                    result['book_id'] = book_id
                    result['content'] = topic_content
                    result['status'] = 'success'
                    result['message'] = 'Topic found successfully'
                    logger.info(f"Topic found in book: {book_name}")
                    return result
                else:
                    logger.debug(f"Topic ###{topic_num}## not found in book: {book_name}")
            
            except Exception as e:
                logger.error(f"Error reading book {book_id}: {str(e)}")
                continue
        
        result['message'] = f"Topic {topic_num} not found in any available books. Checked: {', '.join(books_checked)}"
        logger.warning(result['message'])
        return result
