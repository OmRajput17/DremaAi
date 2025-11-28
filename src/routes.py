"""
Flask API Routes Module
Handles all API route definitions for chunk retrieval
"""
from flask import request, jsonify
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class Routes:
    """Flask API routes handler."""
    
    def __init__(self, app, fetcher, content_processor):
        """
        Initialize routes with Flask app and components.
        
        Args:
            app: Flask application instance
            fetcher: EducationContentFetcher instance
            content_processor: ContentProcessor instance
        """
        self.app = app
        self.fetcher = fetcher
        self.content_processor = content_processor
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes."""
        self.app.add_url_rule('/api/boards', 'get_boards', self.get_boards, methods=['GET'])
        self.app.add_url_rule('/api/classes/<board>', 'get_classes', self.get_classes, methods=['GET'])
        self.app.add_url_rule('/api/subjects/<board>/<class_num>', 'get_subjects', self.get_subjects, methods=['GET'])
        self.app.add_url_rule('/api/topics/<board>/<class_num>/<subject>', 'get_topics', self.get_topics, methods=['GET'])
        self.app.add_url_rule('/api/retrieve_chunks', 'retrieve_chunks', self.retrieve_chunks, methods=['POST'])
    
    def get_boards(self):
        """Get list of available boards."""
        logger.info("GET /api/boards")
        try:
            boards = self.fetcher.get_boards()
            logger.debug(f"Found {len(boards)} boards")
            return jsonify({'success': True, 'boards': boards})
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_classes(self, board):
        """Get classes for a board."""
        logger.info(f"GET /api/classes/{board}")
        try:
            classes = self.fetcher.get_classes(board)
            logger.debug(f"Found {len(classes)} classes")
            return jsonify({'success': True, 'board': board, 'classes': classes})
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_subjects(self, board, class_num):
        """Get subjects for a board and class."""
        logger.info(f"GET /api/subjects/{board}/{class_num}")
        try:
            subjects = self.fetcher.get_subjects(board, class_num)
            logger.debug(f"Found {len(subjects)} subjects")
            return jsonify({'success': True, 'board': board, 'class': class_num, 'subjects': subjects})
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_topics(self, board, class_num, subject):
        """Get topics for a board, class, and subject."""
        logger.info(f"GET /api/topics/{board}/{class_num}/{subject}")
        try:
            topics = self.fetcher.get_topics(board, class_num, subject)
            logger.debug(f"Found {len(topics)} topics")
            return jsonify({'success': True, 'board': board, 'class': class_num, 'subject': subject, 'topics': topics})
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def retrieve_chunks(self):
        """
        Retrieve content chunks based on request parameters.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["1", "2"],
            "num_chunks": 10,
            "difficulty": "medium"
        }
        """
        logger.info("POST /api/retrieve_chunks")
        try:
            data = request.json
            logger.debug(f"Request: {data}")
            
            # Extract parameters
            board = data.get('board')
            class_num = data.get('class')
            subject = data.get('subject')
            topics = data.get('topics', [])
            num_chunks = int(data.get('num_chunks', 10))
            difficulty = data.get('difficulty', 'medium')
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            if not isinstance(topics, list) or len(topics) == 0:
                return jsonify({'success': False, 'error': 'Please provide at least one topic'}), 400
            
            logger.info(f"Retrieving chunks for {len(topics)} topic(s)")
            
            # Fetch and process content
            all_chunks = []
            topic_info_list = []
            
            for topic_num in topics:
                logger.debug(f"Processing topic {topic_num}")
                result = self.fetcher.fetch_content(board, class_num, subject, topic_num)
                
                if result['status'] == 'success':
                    content = result['content']
                    topic_name = result['topic_name']
                    
                    # Extract chunks
                    chunks = self._extract_chunks(content, topic_name, difficulty, num_chunks)
                    
                    # Add metadata
                    for chunk in chunks:
                        chunk['topic_num'] = topic_num
                        chunk['topic_name'] = topic_name
                    
                    all_chunks.extend(chunks)
                    topic_info_list.append({
                        'topic_num': topic_num,
                        'topic_name': topic_name,
                        'book_name': result['book_name'],
                        'chunks_retrieved': len(chunks)
                    })
                else:
                    logger.warning(f"Failed to fetch topic {topic_num}")
                    topic_info_list.append({
                        'topic_num': topic_num,
                        'status': 'failed',
                        'message': result['message']
                    })
            
            if not all_chunks:
                return jsonify({'success': False, 'error': 'Could not retrieve chunks'}), 400
            
            logger.info(f"Retrieved {len(all_chunks)} chunks total")
            
            return jsonify({
                'success': True,
                'metadata': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topics_requested': len(topics),
                    'difficulty': difficulty,
                    'total_chunks': len(all_chunks)
                },
                'topic_info': topic_info_list,
                'chunks': all_chunks
            })
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def _extract_chunks(self, content, topic_name, difficulty, num_chunks):
        """Extract relevant chunks from content."""
        logger.debug(f"Extracting chunks for: {topic_name}")
        
        # Split content into chunks
        chunks = self.content_processor._chunk_content(content)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # If fewer chunks than requested, return all
        if len(chunks) <= num_chunks:
            return [{'content': c.page_content, 'chunk_index': i} for i, c in enumerate(chunks)]
        
        # Use RAG to retrieve most relevant
        try:
            vector_store = self.content_processor._create_vector_store(chunks)
            search_query = self.content_processor._generate_search_query(topic_name, difficulty)
            relevant_chunks = self.content_processor._retrieve_relevant_chunks(vector_store, search_query, num_chunks)
            
            return [{'content': c.page_content, 'chunk_index': i, 'relevance_rank': i+1} for i, c in enumerate(relevant_chunks)]
        
        except Exception as e:
            logger.error(f"RAG error: {str(e)}")
            # Fallback to first N chunks
            return [{'content': c.page_content, 'chunk_index': i} for i, c in enumerate(chunks[:num_chunks])]
