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

    def extract_subtopics(self, content):
        """
        Extract subtopics from content using multiple strategies.
        Returns a list of dicts: [{'id': '8.1', 'name': 'Introduction', 'start': 100}, ...]
        """
        subtopics = []
        
        # Strategy 1: Numbered Sections (e.g., 8.1, 1.2.1)
        # Matches "8.1 Title" or "8 . 1 Title"
        # We look for patterns that start at the beginning of a line
        pattern_numbered = r'(?:^|\n)\s*(\d+(?:\s*\.\s*\d+)+)\s+([^\n]+)'
        
        matches = list(re.finditer(pattern_numbered, content))
        
        if matches:
            for match in matches:
                sub_id = match.group(1).replace(' ', '') # Normalize "8 . 1" to "8.1"
                sub_name = match.group(2).strip()
                start_pos = match.start()
                subtopics.append({
                    'id': sub_id,
                    'name': sub_name,
                    'start': start_pos
                })
        
        # Strategy 2: Explicit Markers (UNIT-X, ##X##) if no numbered sections found or mixed
        # (Sometimes chapters have both, but usually one dominates. We'll append if unique)
        pattern_markers = r'(?:^|\n)\s*(?:UNIT|##)\s*[-]?\s*(\d+)\s*(?:##)?\s*([^\n]*)'
        matches_markers = list(re.finditer(pattern_markers, content, re.IGNORECASE))
        
        for match in matches_markers:
            sub_id = match.group(1).strip()
            sub_name = match.group(2).strip() or f"Unit {sub_id}"
            start_pos = match.start()
            
            # Check if this ID already exists (avoid duplicates)
            if not any(s['id'] == sub_id for s in subtopics):
                subtopics.append({
                    'id': sub_id,
                    'name': sub_name,
                    'start': start_pos
                })

        # Sort by position
        subtopics.sort(key=lambda x: x['start'])
        
        # If no subtopics found, return a single "Full Chapter" item
        if not subtopics:
            subtopics.append({
                'id': 'all',
                'name': 'Full Chapter',
                'start': 0
            })
            
        return subtopics

    def get_subtopics(self, board, class_num, subject, topic_num):
        """
        Get list of subtopics for a given topic.
        """
        # First fetch the full content to parse it
        # We pass subtopics=None to get the full book/chapter content first
        # But wait, fetch_content logic currently extracts a specific topic from a book.
        # We need to get that topic's content first.
        
        # Re-use fetch_content but we need a way to get the RAW topic content without filtering subtopics yet.
        # Actually, fetch_content logic (lines 92+) does exactly that: finds the topic in the book.
        # So we can call fetch_content, get the text, then parse subtopics.
        
        result = self.fetch_content(board, class_num, subject, topic_num)
        
        if result['status'] != 'success':
            return []
            
        content = result['content']
        subtopics = self.extract_subtopics(content)
        
        # Return simplified list for frontend
        return [{'id': s['id'], 'name': s['name']} for s in subtopics]

    def fetch_content(self, board, class_num, subject, topic_num, subtopics=None):
        """
        Fetch the topic content from the appropriate book.
        If subtopics list is provided, filters the content.
        
        Args:
            subtopics (list): Optional list of subtopic IDs to include.
        
        Returns:
            dict: Contains 'book_name', 'book_id', 'topic_name', 'content', and 'status'
        """
        logger.info(f"Fetching content for: Board={board}, Class={class_num}, Subject={subject}, Topic={topic_num}, Subtopics={subtopics}")
        
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
                    
                    # Filter by subtopics if requested
                    if subtopics and isinstance(subtopics, list) and len(subtopics) > 0:
                        all_subtopics = self.extract_subtopics(topic_content)
                        filtered_content = ""
                        
                        # Map IDs to their start/end positions
                        # We need to know where each subtopic ends (which is the start of the next one)
                        for i, sub in enumerate(all_subtopics):
                            if sub['id'] in subtopics or 'all' in subtopics:
                                start = sub['start']
                                # End is start of next subtopic, or end of string
                                end = all_subtopics[i+1]['start'] if i + 1 < len(all_subtopics) else len(topic_content)
                                filtered_content += f"\n\n--- Subtopic {sub['id']} ---\n"
                                filtered_content += topic_content[start:end]
                        
                        if not filtered_content.strip():
                             # Fallback if filtering failed or IDs didn't match
                             logger.warning("Subtopic filtering resulted in empty content. Returning full topic.")
                             result['content'] = topic_content
                        else:
                             result['content'] = filtered_content
                    else:
                        result['content'] = topic_content

                    result['status'] = 'success'
                    result['message'] = 'Topic found successfully'
                    logger.info(f"Topic found in book: {book_name}")
                    logger.info(f"Retrieved Content:\n{result['content']}")
                    return result
                else:
                    logger.debug(f"Topic ###{topic_num}## not found in book: {book_name}")
            
            except Exception as e:
                logger.error(f"Error reading book {book_id}: {str(e)}")
                continue
        
        result['message'] = f"Topic {topic_num} not found in any available books. Checked: {', '.join(books_checked)}"
        logger.warning(result['message'])
        return result
