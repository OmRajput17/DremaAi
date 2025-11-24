"""
Flask Routes Module
Handles all Flask route definitions
"""
from flask import render_template, request, jsonify
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class Routes:
    """Flask routes handler."""
    
    def __init__(self, app, fetcher, mcq_generator):
        """
        Initialize routes with Flask app and components.
        
        Args:
            app: Flask application instance
            fetcher: EducationContentFetcher instance
            mcq_generator: MCQGenerator instance
        """
        self.app = app
        self.fetcher = fetcher
        self.mcq_generator = mcq_generator
        self.register_routes()
    
    def register_routes(self):
        """Register all application routes."""
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/get_classes/<board>', 'get_classes', self.get_classes)
        self.app.add_url_rule('/get_subjects/<board>/<class_num>', 'get_subjects', self.get_subjects)
        self.app.add_url_rule('/get_topics/<board>/<class_num>/<subject>', 'get_topics', self.get_topics)
        self.app.add_url_rule('/generate', 'generate', self.generate, methods=['POST'])
    
    def index(self):
        """Render the main form page."""
        logger.info("GET / - Rendering main page")
        boards = self.fetcher.get_boards()
        logger.debug(f"Found {len(boards)} boards")
        return render_template('index.html', boards=boards)
    
    def get_classes(self, board):
        """Get classes for a selected board."""
        logger.info(f"GET /get_classes/{board}")
        classes = self.fetcher.get_classes(board)
        logger.debug(f"Found {len(classes)} classes for board: {board}")
        return jsonify(classes)
    
    def get_subjects(self, board, class_num):
        """Get subjects for a selected board and class."""
        logger.info(f"GET /get_subjects/{board}/{class_num}")
        subjects = self.fetcher.get_subjects(board, class_num)
        logger.debug(f"Found {len(subjects)} subjects for {board} class {class_num}")
        return jsonify(subjects)
    
    def get_topics(self, board, class_num, subject):
        """Get topics for a selected board, class, and subject."""
        logger.info(f"GET /get_topics/{board}/{class_num}/{subject}")
        topics = self.fetcher.get_topics(board, class_num, subject)
        logger.debug(f"Found {len(topics)} topics for {board} class {class_num} {subject}")
        return jsonify(topics)
    
    def generate(self):
        """Generate MCQs based on form input."""
        logger.info("POST /generate - MCQ generation request received")
        try:
            data = request.json
            logger.debug(f"Request data: {data}")
            
            board = data.get('board')
            class_num = data.get('class')
            subject = data.get('subject')
            topic = data.get('topic')
            num_questions = int(data.get('num_questions', 5))
            difficulty_level = data.get('difficulty_level', 'medium')
            
            # Fetch content
            result = self.fetcher.fetch_content(board, class_num, subject, topic)
            
            if result['status'] != 'success':
                logger.warning(f"Content fetch failed: {result['message']}")
                return jsonify({'error': result['message']}), 400
            
            # Generate MCQs
            mcqs = self.mcq_generator.generate_mcqs(
                num_questions, 
                difficulty_level, 
                result['topic_name'], 
                result['content']
            )
            
            if not mcqs:
                logger.error("MCQ generation failed")
                return jsonify({'error': 'Failed to generate MCQs'}), 500
            
            logger.info(f"Successfully generated {len(mcqs)} MCQs")
            return jsonify({
                'success': True,
                'topic_info': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topic_name': result['topic_name'],
                    'book_name': result['book_name']
                },
                'mcqs': mcqs
            })
        
        except Exception as e:
            logger.error(f"Error in generate endpoint: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500
