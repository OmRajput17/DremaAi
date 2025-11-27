"""
Flask Routes Module
Handles all Flask route definitions
"""
from flask import render_template, request, jsonify, session, redirect, url_for
from src.logging import get_logger
import concurrent.futures

# Initialize logger
logger = get_logger(__name__)


class Routes:
    """Flask routes handler."""
    
    def __init__(self, app, fetcher, mcq_generator, content_processor):
        """
        Initialize routes with Flask app and components.
        
        Args:
            app: Flask application instance
            fetcher: EducationContentFetcher instance
            mcq_generator: MCQGenerator instance
            content_processor: ContentProcessor instance
        """
        self.app = app
        self.fetcher = fetcher
        self.mcq_generator = mcq_generator
        self.content_processor = content_processor
        self.register_routes()
    
    def register_routes(self):
        """Register all application routes."""
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/get_classes/<board>', 'get_classes', self.get_classes)
        self.app.add_url_rule('/get_subjects/<board>/<class_num>', 'get_subjects', self.get_subjects)
        self.app.add_url_rule('/get_topics/<board>/<class_num>/<subject>', 'get_topics', self.get_topics)
        self.app.add_url_rule('/generate', 'generate', self.generate, methods=['POST'])
        self.app.add_url_rule('/results', 'results', self.results, methods=['GET'])
        self.app.add_url_rule('/download_pdf', 'download_pdf', self.download_pdf, methods=['POST'])
    
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
            
            # Handle both single chapter and multiple chapters
            topics = data.get('topics', [])  # Expect list of chapter numbers
            if not isinstance(topics, list):
                # Backward compatibility: single topic/chapter
                single_topic = data.get('topic')
                topics = [single_topic] if single_topic else []
            
            # Validate at least one chapter is selected
            if not topics or len(topics) == 0:
                logger.warning("No chapters selected")
                return jsonify({'error': 'Please select at least one chapter'}), 400
            
            num_questions = int(data.get('num_questions', 5))
            difficulty_level = data.get('difficulty_level', 'medium')
            
            logger.info(f"Generating MCQs for {len(topics)} chapter(s): {topics}")
            
            # Fetch content for all selected chapters
            all_content = []
            topic_names = []
            book_name = None
            
            for topic_num in topics:
                logger.debug(f"Fetching content for chapter {topic_num}")
                result = self.fetcher.fetch_content(board, class_num, subject, topic_num)
                
                if result['status'] == 'success':
                    all_content.append(result['content'])
                    topic_names.append(result['topic_name'])
                    if not book_name:
                        book_name = result['book_name']
                    logger.info(f"Successfully fetched chapter {topic_num}: {result['topic_name']}")
                else:
                    logger.warning(f"Failed to fetch chapter {topic_num}: {result['message']}")
            
            # Check if any content was fetched
            if not all_content:
                logger.error(f"No content found for any of the selected chapters: {topics}")
                return jsonify({'error': f'Could not find content for the selected chapter(s)'}), 400
            
            # Calculate questions distribution
            num_topics = len(all_content)
            base_questions = num_questions // num_topics
            remainder = num_questions % num_topics
            
            mcqs = []
            merged_topic_names = ', '.join(topic_names)
            
            logger.info(f"Processing {num_topics} topics concurrently with ThreadPoolExecutor")
            
            # Prepare arguments for parallel processing
            topic_tasks = []
            for i, (content, topic_name) in enumerate(zip(all_content, topic_names)):
                # Calculate questions for this specific topic
                questions_for_topic = base_questions + (1 if i < remainder else 0)
                
                if questions_for_topic > 0:
                    topic_tasks.append({
                        'content': content,
                        'topic_name': topic_name,
                        'difficulty': difficulty_level,
                        'num_questions': questions_for_topic
                    })
                else:
                    logger.info(f"Skipping topic {topic_name} (0 questions allocated)")

            # Execute tasks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(topic_tasks), 10)) as executor:
                # Submit all tasks
                future_to_topic = {
                    executor.submit(self._process_single_topic, **task): task['topic_name'] 
                    for task in topic_tasks
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_topic):
                    topic_name = future_to_topic[future]
                    try:
                        topic_mcqs = future.result()
                        if topic_mcqs:
                            mcqs.extend(topic_mcqs)
                        else:
                            logger.warning(f"No MCQs generated for topic: {topic_name}")
                    except Exception as exc:
                        logger.error(f"Topic {topic_name} generated an exception: {exc}")

            if not mcqs:
                logger.error("MCQ generation failed for all topics")
                return jsonify({'error': 'Failed to generate MCQs'}), 500
            
            logger.info(f"Successfully generated {len(mcqs)} MCQs across {num_topics} topics")
            
            # Store data in session
            session['mcq_data'] = {
                'success': True,
                'topic_info': {
                    'board': board,
                    'class': class_num,
                    'subject': subject,
                    'topic_name': merged_topic_names,
                    'book_name': book_name,
                    'chapters_selected': len(topic_names)
                },
                'mcqs': mcqs
            }
            
            # Return success response with redirect URL for AJAX
            return jsonify({
                'success': True,
                'redirect': url_for('results')
            })
        
        except Exception as e:
            logger.error(f"Error in generate endpoint: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    def results(self):
        """Render the results page with MCQ data from session."""
        logger.info("GET /results - Rendering results page")
        
        # Get MCQ data from session
        mcq_data = session.get('mcq_data')
        
        if not mcq_data:
            logger.warning("No MCQ data found in session, redirecting to home")
            return redirect(url_for('index'))
        
        logger.info(f"Displaying results with {len(mcq_data.get('mcqs', []))} MCQs")
        return render_template('results.html', data=mcq_data)
    
    def download_pdf(self):
        """Generate and download PDF of MCQs."""
        logger.info("POST /download_pdf - PDF download request received")
        try:
            from flask import send_file, make_response
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            import io
            
            data = request.json
            logger.debug(f"Received MCQ data for PDF: {len(data.get('mcqs', []))} questions")
            
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for PDF elements
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#667eea',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor='#764ba2',
                spaceAfter=12
            )
            
            question_style = ParagraphStyle(
                'Question',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=10
            )
            
            option_style = ParagraphStyle(
                'Option',
                parent=styles['Normal'],
                fontSize=11,
                leftIndent=20,
                spaceAfter=6
            )
            
            answer_style = ParagraphStyle(
                'Answer',
                parent=styles['Normal'],
                fontSize=10,
                textColor='#007bff',
                leftIndent=20,
                spaceAfter=6
            )
            
            # Title
            story.append(Paragraph("📚 MCQ Generator", title_style))
            story.append(Spacer(1, 12))
            
            # Topic Information
            topic_info = data.get('topic_info', {})
            story.append(Paragraph(f"<b>Board:</b> {topic_info.get('board', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Class:</b> {topic_info.get('class', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Subject:</b> {topic_info.get('subject', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Topic:</b> {topic_info.get('topic_name', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Book:</b> {topic_info.get('book_name', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # MCQs
            mcqs = data.get('mcqs', [])
            for index, mcq in enumerate(mcqs, 1):
                # Question
                question_text = f"Q{index}. {mcq.get('question', '')}"
                story.append(Paragraph(question_text, question_style))
                
                # Options
                options = mcq.get('options', {})
                correct_answer = mcq.get('correct_answer', '')
                for key, value in options.items():
                    if key == correct_answer:
                        option_text = f"<b>{key}. {value} ✓</b>"
                    else:
                        option_text = f"{key}. {value}"
                    story.append(Paragraph(option_text, option_style))
                
                # Answer and Explanation
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"<b>Correct Answer:</b> {correct_answer}", answer_style))
                explanation = mcq.get('explanation', 'No explanation provided.')
                story.append(Paragraph(f"<b>Explanation:</b> {explanation}", answer_style))
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"PDF generated successfully with {len(mcqs)} questions")
            
            # Send PDF
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"MCQs_{topic_info.get('subject', 'Unknown')}_{topic_info.get('class', '')}".replace(' ', '_') + '.pdf'
            )
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    def _process_single_topic(self, content, topic_name, difficulty, num_questions):
        """
        Process a single topic: RAG retrieval + MCQ generation.
        Helper method for parallel execution.
        """
        logger.info(f"Processing topic: {topic_name} (Allocated questions: {num_questions})")
        
        # Process content through RAG for focused retrieval
        focused_content = self.content_processor.process_for_mcqs(
            content=content,
            topic_name=topic_name,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        # Generate MCQs for this topic
        return self.mcq_generator.generate_mcqs(
            num_questions, 
            difficulty, 
            topic_name,
            focused_content
        )
