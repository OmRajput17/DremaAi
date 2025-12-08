"""
Flask API Routes Module
Handles all API route definitions for chunk retrieval and question paper generation
"""
from flask import request, jsonify
import json
from src.logging import get_logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils import generate_cbse_prompt, generate_general_prompt, generate_answer_prompt, get_cbse_pattern, generate_summary_prompt, generate_flashcard_prompt, generate_mindmap_prompt, generate_study_tricks_prompt, generate_chat_prompt

# Initialize logger
logger = get_logger(__name__)


class Routes:
    """Flask API routes handler."""
    
    def __init__(self, app, fetcher, content_processor, config):
        """
        Initialize routes with Flask app and components.
        
        Args:
            app: Flask application instance
            fetcher: EducationContentFetcher instance
            content_processor: ContentProcessor instance
            config: Config instance for LLM initialization
        """
        self.app = app
        self.fetcher = fetcher
        self.content_processor = content_processor
        self.config = config
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes."""
        self.app.add_url_rule('/api/boards', 'get_boards', self.get_boards, methods=['GET'])
        self.app.add_url_rule('/api/classes/<board>', 'get_classes', self.get_classes, methods=['GET'])
        self.app.add_url_rule('/api/subjects/<board>/<class_num>', 'get_subjects', self.get_subjects, methods=['GET'])
        self.app.add_url_rule('/api/topics/<board>/<class_num>/<subject>', 'get_topics', self.get_topics, methods=['GET'])
        self.app.add_url_rule('/api/retrieve_chunks', 'retrieve_chunks', self.retrieve_chunks, methods=['POST'])
        self.app.add_url_rule('/api/generate_question_paper', 'generate_question_paper', self.generate_question_paper, methods=['POST'])
        self.app.add_url_rule('/api/summarize', 'generate_summary', self.generate_summary, methods=['POST'])
        self.app.add_url_rule('/api/flash_cards', 'generate_flashcards', self.generate_flashcards, methods=['POST'])
        self.app.add_url_rule('/api/mind_map', 'generate_mindmap', self.generate_mindmap, methods=['POST'])
        self.app.add_url_rule('/api/study_tricks', 'generate_study_tricks', self.generate_study_tricks, methods=['POST'])
        self.app.add_url_rule('/api/generate_answer', 'generate_answer', self.generate_answer, methods=['POST'])
        self.app.add_url_rule('/api/chat_with_ai', 'chat_with_ai', self.chat_with_ai, methods=['POST'])
        self.app.add_url_rule('/api/olympiad', 'generate_olympiad_paper', self.generate_olympiad_paper, methods=['POST'])
    
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

    def generate_question_paper(self):
        """
        Generate question paper by retrieving chunks and using LLM.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": 11,
            "subject": "Physics",
            "topics": ["1", "2"],
            "difficulty": "medium",
            "questionCount": 30,
            "useCBSEPattern": true,
            "customPrompt": "optional custom instructions"
        }
        """
        logger.info("POST /api/generate_question_paper")
        try:
            data = request.json
            logger.debug(f"Request: {data}")
            
            # Extract parameters
            board = data.get('board')
            class_num = int(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            difficulty = data.get('difficulty', 'medium')
            question_count = int(data.get('questionCount', 20))
            use_cbse_pattern = data.get('useCBSEPattern', False)
            custom_prompt = data.get('customPrompt')  # Custom user prompt
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            if not isinstance(topics, list) or len(topics) == 0:
                return jsonify({'success': False, 'error': 'Please provide at least one topic'}), 400
            
            logger.info(f"Generating question paper for {len(topics)} topic(s)")
            
            # Step 1: Retrieve content chunks
            all_content = []
            topic_names = []
            
            for topic_num in topics:
                logger.debug(f"Fetching content for topic {topic_num}")
                result = self.fetcher.fetch_content(board, str(class_num), subject, topic_num)
                
                if result['status'] == 'success':
                    all_content.append(result['content'])
                    topic_names.append(result['topic_name'])
                else:
                    logger.warning(f"Failed to fetch topic {topic_num}: {result['message']}")
            
            if not all_content:
                return jsonify({'success': False, 'error': 'Could not retrieve content for any topic'}), 400
            
            # Combine all content
            combined_content = "\n\n".join(all_content)
            logger.info(f"Combined content length: {len(combined_content)} characters")
            
            # Step 2: Generate prompt
            if use_cbse_pattern and board.upper() == 'CBSE':
                prompt = generate_cbse_prompt(
                    board=board,
                    class_num=class_num,
                    subject=subject,
                    topics=topic_names,
                    content=combined_content,
                    user_prompt=custom_prompt
                )
                
                if prompt is None:
                    # Fallback to general prompt if CBSE pattern not found
                    logger.warning("CBSE pattern not found, using general prompt")
                    prompt = generate_general_prompt(
                        board=board,
                        class_num=class_num,
                        subject=subject,
                        topics=topic_names,
                        difficulty=difficulty,
                        question_count=question_count,
                        user_prompt=custom_prompt
                    )
            else:
                prompt = generate_general_prompt(
                    board=board,
                    class_num=class_num,
                    subject=subject,
                    topics=topic_names,
                    difficulty=difficulty,
                    question_count=question_count,
                    user_prompt=custom_prompt
                )
            
            # Add content to prompt
            full_prompt = prompt + "\n\n" + combined_content
            
            # Step 3: Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm()
            
            logger.info("Generating question paper with GPT-4o...")
            response = llm.invoke(full_prompt)
            
            # Extract content from response
            llm_output = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"LLM response received: {len(llm_output)} characters")
            
            # Try to parse as JSON
            try:
                # Clean the response (remove markdown code blocks if present)
                cleaned_output = llm_output.strip()
                if cleaned_output.startswith('```json'):
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.startswith('```'):
                    cleaned_output = cleaned_output[3:]
                if cleaned_output.endswith('```'):
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()
                
                question_paper = json.loads(cleaned_output)
                
                return jsonify({
                    'success': True,
                    'questionPaper': question_paper,
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topic_names,
                        'difficulty': difficulty,
                        'usedCBSEPattern': use_cbse_pattern and board.upper() == 'CBSE'
                    }
                })
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM output as JSON: {str(e)}")
                # Return raw output if JSON parsing fails
                return jsonify({
                    'success': True,
                    'questionPaper': {'raw_output': llm_output},
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topic_names,
                        'difficulty': difficulty,
                        'warning': 'Output was not valid JSON, returning raw text'
                    }
                })
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def generate_answer(self):
        """
        Generate answer key for a question paper.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": 11,
            "subject": "Physics",
            "topics": ["1", "2"],
            "questions": {...},  # Question paper JSON object
            "content": "...",     # Optional, will fetch if not provided
            "useCBSEPattern": true
        }
        """
        logger.info("POST /api/generate_answer")
        try:
            data = request.json
            logger.debug(f"Request: {data}")
            
            # Extract parameters
            board = data.get('board')
            class_num = int(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            questions = data.get('questions')
            content = data.get('content')
            use_cbse_pattern = data.get('useCBSEPattern', False)
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            if not questions:
                return jsonify({'success': False, 'error': 'Questions parameter is required'}), 400
            if not isinstance(topics, list) or len(topics) == 0:
                return jsonify({'success': False, 'error': 'Please provide at least one topic'}), 400
            
            logger.info(f"Generating answers for {len(topics)} topic(s)")
            
            # Step 1: Retrieve content if not provided
            if not content:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                topic_names = []
                
                for topic_num in topics:
                    logger.debug(f"Fetching content for topic {topic_num}")
                    result = self.fetcher.fetch_content(board, str(class_num), subject, topic_num)
                    
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                        topic_names.append(result['topic_name'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}: {result['message']}")
                
                if not all_content:
                    return jsonify({'success': False, 'error': 'Could not retrieve content for any topic'}), 400
                
                # Combine all content
                content = "\n\n".join(all_content)
            else:
                # If content provided, still need topic names
                topic_names = [f"Topic {t}" for t in topics]
            
            logger.info(f"Content length: {len(content)} characters")
            
            # Step 2: Generate prompt
            prompt = generate_answer_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topic_names,
                questions=questions,
                content=content,
                use_cbse_pattern=use_cbse_pattern
            )
            
            # Step 3: Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm()
            
            logger.info("Generating answer key with GPT-4o...")
            response = llm.invoke(prompt)
            
            # Extract content from response
            llm_output = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"LLM response received: {len(llm_output)} characters")
            
            # Try to parse as JSON
            try:
                # Clean the response (remove markdown code blocks if present)
                cleaned_output = llm_output.strip()
                if cleaned_output.startswith('```json'):
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.startswith('```'):
                    cleaned_output = cleaned_output[3:]
                if cleaned_output.endswith('```'):
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()
                
                answer_key = json.loads(cleaned_output)
                
                return jsonify({
                    'success': True,
                    'answerKey': answer_key,
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topic_names,
                        'usedCBSEPattern': use_cbse_pattern
                    }
                })
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM output as JSON: {str(e)}")
                # Return raw output if JSON parsing fails
                return jsonify({
                    'success': True,
                    'answerKey': {'raw_output': llm_output},
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topic_names,
                        'warning': 'Output was not valid JSON, returning raw text'
                    }
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
    
    def _intelligent_content_filter(self, content: str, topics: list, max_chars: int = 12000) -> str:
        """
        Intelligently reduce content size using RAG instead of blind truncation.
        
        Args:
            content (str): Full content
            topics (list): List of topic names/numbers
            max_chars (int): Target maximum characters
            
        Returns:
            str: Filtered content with most relevant parts
        """
        if len(content) <= max_chars:
            return content
            
        logger.info(f"Content size {len(content)} chars exceeds {max_chars}, using RAG to filter...")
        
        try:
            # Use RAG to extract most relevant chunks
            topic_name = " & ".join([str(t) for t in topics]) if isinstance(topics, list) else str(topics)
            focused_content = self.content_processor.process_for_mcqs(
                content=content,
                topic_name=topic_name,
                difficulty="medium",
                num_questions=10  # Gets ~10 best chunks
            )
            logger.info(f"RAG filtered content to {len(focused_content)} chars ({100*(1-len(focused_content)/len(content)):.1f}% reduction)")
            return focused_content
        except Exception as e:
            logger.error(f"RAG filtering failed: {e}, falling back to truncation")
            return content[:max_chars] + "\n\n[Content truncated]"

    def generate_summary(self):
        """
        Generate chapter summary.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["Force"],
            "content": "Full chapter content..."
        }
        """
        logger.info("POST /api/summarize")
        try:
            data = request.json
            logger.debug(f"Request keys: {list(data.keys())}")
            
            # Extract parameters
            board = data.get('board')
            class_num = str(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            content = data.get('content')
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
            # Fetch content if not provided
            if not content:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                for topic_num in topics:
                    # Ensure topic is string if needed, fetcher expects it
                    result = self.fetcher.fetch_content(board, class_num, subject, str(topic_num))
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}")
                
                if not all_content:
                    return jsonify({'success': False, 'error': 'Could not retrieve content'}), 400
                
                content = "\n\n".join(all_content)
            
            content = self._intelligent_content_filter(content, topics, max_chars=15000)
            
            logger.info(f"Generating summary for {subject} Class {class_num}")
            
            # Generate prompt
            prompt = generate_summary_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topics,
                content=content
            )
            
            # Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm()
            
            logger.info("Generating summary with GPT-4o...")
            response = llm.invoke(prompt)
            
            # Extract content
            summary = response.content if hasattr(response, 'content') else str(response)
            
            return jsonify({
                'success': True,
                'summary': summary,
                'metadata': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topics': topics
                }
            })
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def generate_flashcards(self):
        """
        Generate flashcards.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["Chemical Reactions"],
            "content": "Optional content...",
            "cardCount": 15
        }
        """
        logger.info("POST /api/flash_cards")
        try:
            data = request.json
            logger.debug(f"Request keys: {list(data.keys())}")
            
            # Extract parameters
            board = data.get('board')
            class_num = str(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            content = data.get('content')
            card_count = int(data.get('cardCount', 15))
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
            # Fetch content if not provided
            if not content:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                for topic_num in topics:
                    # Ensure topic is string if needed, fetcher expects it
                    result = self.fetcher.fetch_content(board, class_num, subject, str(topic_num))
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}")
                
                if not all_content:
                    return jsonify({'success': False, 'error': 'Could not retrieve content'}), 400
                
                content = "\n\n".join(all_content)
            
            content = self._intelligent_content_filter(content, topics, max_chars=15000)
            
            logger.info(f"Generating {card_count} flashcards for {subject} Class {class_num}")
            
            # Generate prompt
            prompt = generate_flashcard_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topics,
                content=content,
                card_count=card_count
            )
            
            # Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm(model_name="gpt-4o-mini")
            
            logger.info("Generating flashcards with GPT-4o-mini...")
            response = llm.invoke(prompt)
            
            # Extract content
            llm_output = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON
            try:
                # Clean the response (remove markdown code blocks if present)
                cleaned_output = llm_output.strip()
                if cleaned_output.startswith('```json'):
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.startswith('```'):
                    cleaned_output = cleaned_output[3:]
                if cleaned_output.endswith('```'):
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()
                
                flashcards = json.loads(cleaned_output)
                
                return jsonify({
                    'success': True,
                    'flashcards': flashcards,
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topics,
                        'count': len(flashcards)
                    }
                })
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM output as JSON: {str(e)}")
                # Return raw output if JSON parsing fails, but wrapped in a structure
                return jsonify({
                    'success': False, 
                    'error': 'Failed to parse generated flashcards',
                    'raw_output': llm_output
                }), 500
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def generate_mindmap(self):
        """
        Generate mind map.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["Chemical Reactions"],
            "content": "Optional content..."
        }
        """
        logger.info("POST /api/mind_map")
        try:
            data = request.json
            logger.debug(f"Request keys: {list(data.keys())}")
            
            # Extract parameters
            board = data.get('board')
            class_num = str(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            content = data.get('content')
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
            # Fetch content if not provided
            if not content:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                for topic_num in topics:
                    # Ensure topic is string if needed, fetcher expects it
                    result = self.fetcher.fetch_content(board, class_num, subject, str(topic_num))
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}")
                
                if not all_content:
                    return jsonify({'success': False, 'error': 'Could not retrieve content'}), 400
                
                content = "\n\n".join(all_content)
            
            content = self._intelligent_content_filter(content, topics, max_chars=15000)
            
            logger.info(f"Generating mind map for {subject} Class {class_num}")
            
            # Generate prompt
            prompt = generate_mindmap_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topics,
                content=content
            )
            
            # Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm(model_name="gpt-4o-mini")
            
            logger.info("Generating mind map with GPT-4o-mini...")
            response = llm.invoke(prompt)
            
            # Extract content
            llm_output = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON
            try:
                # Clean the response (remove markdown code blocks if present)
                cleaned_output = llm_output.strip()
                if cleaned_output.startswith('```json'):
                    cleaned_output = cleaned_output[7:]
                if cleaned_output.startswith('```'):
                    cleaned_output = cleaned_output[3:]
                if cleaned_output.endswith('```'):
                    cleaned_output = cleaned_output[:-3]
                cleaned_output = cleaned_output.strip()
                
                mindmap_data = json.loads(cleaned_output)
                
                return jsonify({
                    'success': True,
                    'mindmap': mindmap_data,
                    'metadata': {
                        'board': board,
                        'class': class_num,
                        'subject': subject,
                        'topics': topics
                    }
                })
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM output as JSON: {str(e)}")
                # Return raw output if JSON parsing fails
                return jsonify({
                    'success': False, 
                    'error': 'Failed to parse generated mind map',
                    'raw_output': llm_output
                }), 500
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def generate_study_tricks(self):
        """
        Generate study tricks and mnemonics.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["Chemical Reactions"],
            "content": "Optional content..."
        }
        """
        logger.info("POST /api/study_tricks")
        try:
            data = request.json
            logger.debug(f"Request keys: {list(data.keys())}")
            
            # Extract parameters
            board = data.get('board')
            class_num = str(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            content = data.get('content')
            
            # Validate
            if not all([board, class_num, subject]):
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
            # Fetch content if not provided
            if not content:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                for topic_num in topics:
                    # Ensure topic is string if needed, fetcher expects it
                    result = self.fetcher.fetch_content(board, class_num, subject, str(topic_num))
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}")
                
                if not all_content:
                    return jsonify({'success': False, 'error': 'Could not retrieve content'}), 400
                
                content = "\n\n".join(all_content)
            
            content = self._intelligent_content_filter(content, topics, max_chars=15000)
            
            logger.info(f"Generating study tricks for {subject} Class {class_num}")
            
            # Generate prompt
            prompt = generate_study_tricks_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topics,
                content=content
            )
            
            # Call LLM
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm(model_name="gpt-4o-mini")
            
            logger.info("Generating study tricks with GPT-4o-mini...")
            response = llm.invoke(prompt)
            
            # Extract content
            tricks = response.content if hasattr(response, 'content') else str(response)
            
            return jsonify({
                'success': True,
                'tricks': tricks,
                'metadata': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topics': topics
                }
            })
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def chat_with_ai(self):
        """
        Chat with AI tutor service with conversation history support.
        
        Expected JSON body:
        {
            "board": "CBSE",
            "class": "10",
            "subject": "Science",
            "topics": ["Force"],
            "message": "Can you explain Newton's third law?",
            "conversationHistory": [
                {
                    "role": "user",
                    "content": "What is force?",
                    "timestamp": "2024-12-04T10:00:00Z"
                },
                {
                    "role": "assistant",
                    "content": "Force is...",
                    "timestamp": "2024-12-04T10:00:05Z"
                }
            ],
            "content": "Optional textbook content..."
        }
        """
        logger.info("POST /api/chat_with_ai")
        try:
            data = request.json
            logger.debug(f"Request keys: {list(data.keys())}")
            
            # Extract parameters
            board = data.get('board')
            class_num = str(data.get('class'))
            subject = data.get('subject')
            topics = data.get('topics', [])
            message = data.get('message')
            conversation_history = data.get('conversationHistory', [])
            content = data.get('content')
            
            # Validate required fields
            if not all([board, class_num, subject, message]):
                return jsonify({'success': False, 'error': 'Missing required parameters: board, class, subject, message'}), 400
            
            logger.info(f"Chat request for {subject} Class {class_num}, history length: {len(conversation_history)}")
            
            # Fetch content if not provided
            if not content and topics:
                logger.info("Content not provided, fetching from source...")
                all_content = []
                for topic_num in topics:
                    # Ensure topic is string if needed, fetcher expects it
                    result = self.fetcher.fetch_content(board, class_num, subject, str(topic_num))
                    if result['status'] == 'success':
                        all_content.append(result['content'])
                    else:
                        logger.warning(f"Failed to fetch topic {topic_num}")
                
                if all_content:
                    content = "\n\n".join(all_content)
                    logger.info(f"Fetched content: {len(content)} characters")
                else:
                    logger.warning("Could not retrieve content, proceeding without textbook reference")
                    content = None
            
            # Apply intelligent content filtering if content is provided
            if content:
                content = self._intelligent_content_filter(content, topics, max_chars=12000)
                logger.info(f"Filtered content: {len(content)} characters")
            
            # Generate chat prompt
            prompt = generate_chat_prompt(
                board=board,
                class_num=class_num,
                subject=subject,
                topics=topics if topics else [subject],
                message=message,
                conversation_history=conversation_history,
                content=content
            )
            
            # Call LLM (using gpt-4o-mini for faster, cost-effective chat responses)
            logger.info("Initializing LLM...")
            llm = self.config.initialize_llm(model_name="gpt-4o-mini")
            
            logger.info("Generating chat response with GPT-4o-mini...")
            response = llm.invoke(prompt)
            
            # Extract content
            ai_response = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Chat response generated: {len(ai_response)} characters")
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'metadata': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topics': topics,
                    'conversationLength': len(conversation_history) + 2  # +2 for current exchange
                }
            })
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    def generate_olympiad_paper(self):
        """
        Generate Olympiad question paper using sample paper as reference.
        
        Expected JSON body:
        {
            "grade": "4",
            "subject": "MATHS"
        }
        """
        logger.info("POST /api/olympiad")
        
        try:
            data = request.get_json()
            grade = data.get('grade')
            subject = data.get('subject')
            
            # Validate required fields
            if not grade or not subject:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields: grade and subject'
                }), 400
            
            logger.info(f"Generating Olympiad paper for Grade {grade} {subject}")
            
            # Initialize olympiad fetcher
            from src.components.olympiad_fetcher import OlympiadFetcher
            olympiad_fetcher = OlympiadFetcher()
            
            # Check if sample paper exists
            if not olympiad_fetcher.validate_paper_exists(grade, subject):
                available_subjects = olympiad_fetcher.get_available_subjects(grade)
                return jsonify({
                    'success': False,
                    'error': f'Sample paper not found for Grade {grade} {subject}',
                    'availableSubjects': available_subjects
                }), 404
            
            # Get sample paper content
            try:
                sample_paper = olympiad_fetcher.get_sample_paper(grade, subject)
            except FileNotFoundError as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 404
            except Exception as e:
                logger.error(f"Error reading sample paper: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to read sample paper: {str(e)}'
                }), 500
            
            # Generate prompt using sample paper
            from src.utils.prompt_generator import generate_olympiad_prompt
            prompt = generate_olympiad_prompt(grade, subject, sample_paper)
            
            # Initialize LLM
            llm = self.config.initialize_llm(model_name="gpt-4o-mini")  # Use mini for speed
            
            # Generate Olympiad paper
            logger.info("Calling LLM to generate Olympiad paper")
            response = llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            logger.debug(f"LLM response length: {len(response_text)} characters")
            
            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                json_text = response_text.strip()
                if json_text.startswith('```json'):
                    json_text = json_text[7:]
                if json_text.startswith('```'):
                    json_text = json_text[3:]
                if json_text.endswith('```'):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                olympiad_paper = json.loads(json_text)
                
                logger.info(f"Successfully generated Olympiad paper with {olympiad_paper.get('totalQuestions', 0)} questions")
                
                return jsonify({
                    'success': True,
                    'olympiadPaper': olympiad_paper
                })
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.debug(f"Response text: {response_text[:500]}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to parse LLM response as JSON',
                    'details': str(e)
                }), 500
                
        except Exception as e:
            logger.error(f"Error generating Olympiad paper: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }), 500

