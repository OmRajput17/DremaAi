"""
Content Fetcher Component
Handles fetching educational content from data files
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class EducationContentFetcher:
    """Fetches educational content based on board, class, subject, and topic."""

    def __init__(self, category_file: str = 'category.json', topics_file: str = 'topics.json', data_folder: str = 'data'):
        """
        Initialize the content fetcher with JSON index files and a data folder.

        Expected file structures:
        - category.json: Boards -> [BoardName] -> Classes -> [ClassNum] -> Subjects -> [SubjectName] -> Books
        - topics.json: [BoardName] -> [ClassNum] -> [SubjectName] -> {topic_num: topic_name}
        """
        logger.info("Initializing EducationContentFetcher...")
        self.data_folder = Path(data_folder)

        # Load JSON files (safe)
        self.category_data: Dict[str, Any] = {}
        self.topics_data: Dict[str, Any] = {}

        try:
            with open(category_file, 'r', encoding='utf-8') as f:
                self.category_data = json.load(f)
        except FileNotFoundError:
            logger.error("category.json not found at '%s'. Continuing with empty category data.", category_file)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode category.json: %s", e)

        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                self.topics_data = json.load(f)
        except FileNotFoundError:
            logger.error("topics.json not found at '%s'. Continuing with empty topics data.", topics_file)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode topics.json: %s", e)

        # Normalize keys to make lookups robust
        self._normalize_category_data()
        self._normalize_topics_data()

        logger.info("EducationContentFetcher initialized successfully")

    def _normalize_category_data(self) -> None:
        """
        Normalize category_data structure for case-insensitive lookups.
        Transforms boards and subject keys to lowercase and class numbers to string keys.
        """
        raw = self.category_data or {}
        normalized: Dict[str, Any] = {'boards': {}}
        boards = raw.get('Boards', {})
        for board_name, board_val in boards.items():
            bkey = board_name.strip().lower()
            normalized['boards'][bkey] = {}
            classes = board_val.get('Classes', {})
            normalized['boards'][bkey]['classes'] = {}
            for class_key, class_val in classes.items():
                ckey = str(class_key).strip()
                normalized_subjects = {}
                subjects = class_val.get('Subjects', {})
                for subj_name, subj_val in subjects.items():
                    skey = subj_name.strip().lower()
                    normalized_subjects[skey] = subj_val
                normalized['boards'][bkey]['classes'][ckey] = {'subjects': normalized_subjects}
        self._normalized_category = normalized

    def _normalize_topics_data(self) -> None:
        """
        Normalize topics_data for case-insensitive lookups:
        boards lowercased, class numbers as strings, subject lowercased.
        """
        raw = self.topics_data or {}
        normalized: Dict[str, Any] = {}
        for board_name, classes in raw.items():
            bkey = board_name.strip().lower()
            normalized[bkey] = {}
            for class_key, subjects in classes.items():
                ckey = str(class_key).strip()
                normalized[bkey].setdefault(ckey, {})
                for subj_name, topics in subjects.items():
                    skey = subj_name.strip().lower()
                    normalized[bkey][ckey][skey] = {str(k): v for k, v in topics.items()}
        self._normalized_topics = normalized

    def get_boards(self) -> List[str]:
        """Get list of available boards (normalized)."""
        return list(self._normalized_category.get('boards', {}).keys())

    def get_classes(self, board: str) -> List[str]:
        """Get list of available classes for a board."""
        b = self._normalized_category.get('boards', {}).get(board.strip().lower(), {})
        return list(b.get('classes', {}).keys())

    def get_subjects(self, board: str, class_num: int) -> List[str]:
        """Get list of available subjects for a board and class (normalized subject names)."""
        b = self._normalized_category.get('boards', {}).get(board.strip().lower(), {})
        c = b.get('classes', {}).get(str(class_num), {})
        return list(c.get('subjects', {}).keys())

    def get_topics(self, board: str, class_num: int, subject: str) -> Dict[str, str]:
        """
        Get list of available topics for a board, class, and subject.

        topics.json structure (normalized): board -> class_num -> subject -> {topic_num: topic_name}
        """
        board_key = board.strip().lower()
        class_key = str(class_num)
        subject_key = subject.strip().lower()
        topics = self._normalized_topics.get(board_key, {}).get(class_key, {}).get(subject_key, {})
        logger.debug("Retrieved topics for %s/%s/%s: %d topics found", board_key, class_key, subject_key, len(topics))
        return {num: name for num, name in topics.items()}

    def get_books(self, board: str, class_num: int, subject: str) -> List[Dict[str, Any]]:
        """
        Get list of books (as dicts) for a board, class, and subject.
        Returns list of book mapping objects preserving book_id and Name if present.
        """
        board_key = board.strip().lower()
        class_key = str(class_num).strip()
        subject_key = subject.strip().lower()
        subj = self._normalized_category.get('boards', {}).get(board_key, {}).get('classes', {}).get(class_key, {}).get('subjects', {}).get(subject_key, {})
        books_container = subj.get('Books', {}) if isinstance(subj, dict) else {}
        if isinstance(books_container, dict):
            return [val for val in books_container.values()]
        elif isinstance(books_container, list):
            return books_container
        else:
            return []

    def extract_topic_from_book(self, book_content: str, topic_num: Any) -> Optional[str]:
        """
        Extract topic ONLY when chapter is marked as:
            1. ##x##
            2. UNIT-x / Unit-x / unit-x  (dash or whitespace allowed)
        Stops when next UNIT-x or ##x## marker or EOF is reached.
        """
        topic_num = str(topic_num).strip()

        # Stop when next UNIT-x or ##x## or end of file
        next_marker = rf'(?=(?:UNIT(?:\s*-\s*|\s+)\d+|##\s*\d+\s*##|\Z))'

        patterns = [
            rf'##\s*{re.escape(topic_num)}\s*##\s*(.*?){next_marker}',
            rf'UNIT(?:\s*-\s*|\s+){re.escape(topic_num)}\s*(.*?){next_marker}',
        ]

        flags = re.IGNORECASE | re.DOTALL

        for pat in patterns:
            match = re.search(pat, book_content, flags)
            if match:
                return match.group(1).strip()

        return None

    def fetch_content(self, board: str, class_num: int, subject: str, topic_num: Any) -> Dict[str, Any]:
        """
        Fetch the topic content from the appropriate book.

        Returns:
            dict: {
                'board', 'class', 'subject', 'topic_num',
                'book_name', 'book_id', 'topic_name', 'content',
                'status' ('success' | 'error'), 'message'
            }
        """
        logger.info("Fetching content for: Board=%s, Class=%s, Subject=%s, Topic=%s", board, class_num, subject, topic_num)

        result: Dict[str, Any] = {
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

        # Try to resolve a topic name from topics.json (optional)
        topics = self.get_topics(board, class_num, subject)
        if topics and str(topic_num) in topics:
            result['topic_name'] = topics[str(topic_num)]
            logger.debug("Topic name found: %s", result['topic_name'])
        else:
            result['topic_name'] = f"Topic {topic_num}"
            logger.debug("Topic name not found in topics.json, using default: %s", result['topic_name'])

        # Get books for this subject (list of dicts)
        books = self.get_books(board, class_num, subject)
        if not books:
            result['message'] = "No books found for this subject in category.json"
            logger.warning(result['message'])
            return result

        logger.info("Searching in %d book(s)...", len(books))

        books_checked: List[str] = []
        for book in books:
            # Expect book to be a dict with keys 'book_id' and 'Name' or similar
            book_id = book.get('book_id') or book.get('id') or book.get('bookId') or None
            book_name = book.get('Name') or book.get('name') or f"Book-{book_id}"
            if not book_id:
                logger.debug("Skipping book entry without book_id: %s", book)
                continue

            safe_book_id = Path(str(book_id)).name
            book_path = self.data_folder / f"{safe_book_id}.txt"

            books_checked.append(str(safe_book_id))
            logger.debug("Checking book: %s (ID: %s) at path %s", book_name, safe_book_id, book_path)

            if not book_path.exists():
                logger.debug("Book file not found: %s", book_path)
                continue

            try:
                book_content = book_path.read_text(encoding='utf-8')
                topic_content = self.extract_topic_from_book(book_content, topic_num)

                if topic_content:
                    result['book_name'] = book_name
                    result['book_id'] = safe_book_id
                    result['content'] = topic_content
                    result['status'] = 'success'
                    result['message'] = 'Topic found successfully'
                    logger.info("Topic found in book: %s", book_name)
                    return result
                else:
                    logger.debug("Topic marker for %s not found in book: %s", topic_num, book_name)

            except Exception as e:
                logger.error("Error reading book %s: %s", safe_book_id, e)
                continue

        result['message'] = f"Topic {topic_num} not found in any available books. Checked: {', '.join(books_checked)}"
        logger.warning(result['message'])
        return result
