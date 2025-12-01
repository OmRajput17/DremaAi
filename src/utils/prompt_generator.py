"""
Prompt Generator for Question Paper Generation
Handles generation of prompts for different subjects and CBSE patterns
"""
from typing import Dict, List, Optional
from src.utils.cbse_patterns import get_cbse_pattern, CBSEPattern
from src.logging import get_logger

logger = get_logger(__name__)


def generate_cbse_prompt(
    board: str,
    class_num: int,
    subject: str,
    topics: List[str],
    content: str,
    generate_answers: bool = False,
    questions_text: Optional[str] = None
) -> Optional[str]:
    """
    Generate prompt for CBSE question paper generation.
    
    Args:
        board: Educational board (e.g., 'CBSE')
        class_num: Class number (e.g., 11)
        subject: Subject name (e.g., 'Physics')
        topics: List of topic names
        content: Educational content from textbook
        generate_answers: Whether to generate answer key
        questions_text: Question paper text (for answer key generation)
    
    Returns:
        Generated prompt string or None if pattern not found
    """
    # If generating answers
    if generate_answers and questions_text:
        return f"""You are an experienced CBSE teacher creating answer keys.

Generate comprehensive answers for this question paper following CBSE marking scheme format.

Question Paper:
{questions_text}

Topics: {', '.join(topics)}
Subject: {subject}
Class: {class_num}

IMPORTANT: Return your response as a valid JSON object with this structure:
{{
  "answerKey": [
    {{
      "section": "Section A",
      "answers": [
        {{"questionNumber": 1, "answer": "detailed answer text", "marks": 1}},
        {{"questionNumber": 2, "answer": "detailed answer text", "marks": 1}}
      ]
    }}
  ]
}}

Instructions:
- Provide step-by-step solutions for all questions
- For MCQs, explain why the correct option is right
- For descriptive questions, provide comprehensive explanations with proper formatting
- Follow CBSE marking scheme guidelines
- Be pedagogically sound and educational"""
    
    # Get CBSE pattern
    cbse_pattern = get_cbse_pattern(subject, class_num)
    
    if not cbse_pattern:
        logger.warning(f"CBSE pattern not found for {subject} Class {class_num}, falling back to default pattern")
        return None
    
    # Generate sections description
    sections_description = "\n\n".join([
        f"{idx + 1}. **{section.name}** ({section.questions} questions, {section.marks_per_question} marks each, {section.total_marks} marks total)\n   - {section.description}"
        for idx, section in enumerate(cbse_pattern.sections)
    ])
    
    return f"""You are an experienced CBSE teacher creating a question paper for Class {class_num} {subject}.

**Exam Pattern Details:**
- Total Marks: {cbse_pattern.total_marks}
- Time: {cbse_pattern.time_limit} minutes
- Board: {board}
- Topics: {', '.join(topics)}

**Section Structure:**
{sections_description}

**Context from NCERT Textbook:**
{content}

CRITICAL INSTRUCTIONS:
1. Follow the EXACT section structure provided above
2. Generate questions STRICTLY from the provided textbook content and topics
3. Ensure questions are age-appropriate for Class {class_num}
4. Include competency-based questions (CBQs) as per CBSE guidelines
5. For MCQs, provide 4 options with clear correct answers
6. Return ONLY valid JSON, no additional text

**REQUIRED JSON FORMAT:**
{{
  "questionPaper": {{
    "title": "Class {class_num} {subject} Question Paper",
    "totalMarks": {cbse_pattern.total_marks},
    "duration": {cbse_pattern.time_limit},
    "sections": [
      {{
        "sectionName": "Section A: MCQs & Assertion-Reason",
        "questions": [
          {{
            "questionNumber": 1,
            "question": "question text here",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correctAnswer": "A",
            "marks": 1
          }}
        ]
      }}
    ]
  }}
}}

Generate the complete question paper in JSON format:"""


def generate_general_prompt(
    board: str,
    class_num: int,
    subject: str,
    topics: List[str],
    difficulty: str,
    question_count: int,
    generate_answers: bool = False,
    questions_text: Optional[str] = None
) -> str:
    """
    Generate prompt for general question paper (non-CBSE or custom format).
    
    Args:
        board: Educational board
        class_num: Class number
        subject: Subject name
        topics: List of topic names
        difficulty: Difficulty level (easy/medium/hard)
        question_count: Total number of questions
        generate_answers: Whether to generate answer key
        questions_text: Question paper text (for answer key generation)
    
    Returns:
        Generated prompt string
    """
    # If generating answers
    if generate_answers and questions_text:
        return f"""You are an experienced teacher providing detailed answer keys. Generate comprehensive answers for the following question paper.

Question Paper:
{questions_text}

Topics: {', '.join(topics)}
Subject: {subject}
Class: {class_num}

Instructions:
- Provide detailed, accurate answers for each question
- For MCQs, explain why the correct option is right
- For descriptive questions, provide comprehensive explanations
- Use clear formatting with question numbers
- Be pedagogically sound and educational

Generate the answer key:"""
    
    # Subject-specific prompts
    subject_lower = subject.lower()
    
    # Mathematics
    if subject_lower in ['maths', 'mathematics', 'math']:
        return f"""You are an intelligent and experienced teacher with a deep understanding of the provided topics and context. Your task is to create a comprehensive question paper based on the details such as class, subject, and topics provided to you.

The question paper should be mathematical in nature and do not ask questions based on any visual representation or story from the book, so that students can solve it based on their ability without depending on a book.

Details:
- Board: {board}
- Class: {class_num}
- Subject: {subject}
- Topics: {', '.join(topics)}
- Difficulty Level: {difficulty}
- Total Questions: {question_count}

Structure the question paper as follows:
1. Word Problems ({question_count // 6} questions): Mathematical problems presented through stories or real-life situations. These should encourage problem-solving and critical thinking.
2. Multiple Choice Questions ({question_count // 6} questions): Provide four options with only one correct answer.
3. Fill in the Blanks ({question_count // 6} questions): Use statements from the chapter, asking to fill in the missing words.
4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
5. Match the Following ({question_count // 6} questions): Pairs of items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
6. Story-Based Problems ({question_count - 5 * (question_count // 6)} questions): Provide a story from which students must extract data to solve a mathematical problem. These problems should be engaging and contextually relevant.

Context:"""
    
    # English Grammar
    elif subject_lower in ['english grammar', 'grammar']:
        return f"""You are an intelligent and experienced teacher with a deep understanding of the provided topics and context. Your task is to create a comprehensive question paper based on the details such as class, subject, and topics provided to you.

The question paper should be practical in nature and ask questions with relations to application of grammatical concepts and not theory or definitions, so that students can solve it based on their ability and learn the applications.

Details:
- Board: {board}
- Class: {class_num}
- Subject: {subject}
- Topics: {', '.join(topics)}
- Difficulty Level: {difficulty}
- Total Questions: {question_count}

Structure the question paper as follows:
1. Comprehensive Questions ({question_count // 6} questions): Provide a paragraph and ask grammatical questions related to it. There will be only one paragraph from which you will be asking the questions.
2. Multiple Choice Questions ({question_count // 6} questions): Provide four options with only one correct answer.
3. Fill in the Blanks ({question_count // 6} questions): Use statements from the chapter, asking to fill in the missing words.
4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
5. Match the Following ({question_count // 6} questions): Pairs of items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Ask for the meanings of words used in the chapter.

Context:"""
    
    # Hindi / Hindi Grammar
    elif subject_lower in ['hindi', 'hindi grammar']:
        if subject_lower == 'hindi':
            structure = f"""1. Descriptive Questions ({question_count // 6} questions): Questions that require detailed explanations
2. MCQ Questions ({question_count // 6} questions): Multiple-choice questions with one correct answer out of four options.
3. Fill in the Blanks ({question_count // 6} questions): Statements with missing words to be filled based on the chapter.
4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
5. Match the Following ({question_count // 6} questions): Pairs of related items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Questions asking for the meaning of words used in the chapter.

Question Paper should be in Hindi language and start directly with descriptive questions without providing any instructions."""
        else:
            structure = f"""1. Comprehensive Questions ({question_count // 6} questions): Provide one paragraph only and ask grammatical questions related to it.
2. MCQ Questions ({question_count // 6} questions): Multiple-choice questions with one correct answer out of four options.
3. Fill in the Blanks ({question_count // 6} questions): Statements with missing words to be filled based on the chapter.
4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
5. Match the Following ({question_count // 6} questions): Pairs of related items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Questions asking for the meaning of words used in the chapter.

Question Paper should be in Hindi language and start directly with descriptive questions without providing any instructions."""
        
        return f"""You are an intelligent and experienced teacher with a deep understanding of the provided topics and context. Your task is to create a comprehensive question paper based on the details such as class, subject, and topics provided to you. Follow the context strictly and ensure the questions reflect the topics accurately without adding any personal interpretations.

Details:
- Board: {board}
- Class: {class_num}
- Subject: {subject}
- Topics: {', '.join(topics)}
- Difficulty Level: {difficulty}
- Total Questions: {question_count}

Structure the question paper as follows:
{structure}

Context:"""
    
    # Default/General subjects
    else:
        return f"""You are an intelligent and experienced teacher creating a comprehensive question paper for Class {class_num} {subject}.

Details:
- Board: {board}
- Class: {class_num}
- Subject: {subject}
- Topics: {', '.join(topics)}
- Difficulty Level: {difficulty}
- Total Questions: {question_count}

Based on the provided context, create a well-structured question paper with the following sections:

1. **Descriptive Questions** ({question_count // 6} questions): Questions requiring detailed explanations
2. **Multiple Choice Questions** ({question_count // 6} questions): Four options with one correct answer
3. **Fill in the Blanks** ({question_count // 6} questions): Statements with missing words
4. **True or False** ({question_count // 6} questions): Statements to be marked as true or false
5. **Match the Following** ({question_count // 6} questions): Pairs of items to be matched correctly
6. **Short Answer Questions** ({question_count - 5 * (question_count // 6)} questions): Brief explanations required

Requirements:
- Ensure questions are age-appropriate for Class {class_num}
- Maintain {difficulty.lower()} difficulty level throughout
- Focus strictly on the provided topics: {', '.join(topics)}
- Use clear, unambiguous language
- For MCQs, ensure only one option is clearly correct
- For Match the Following, scramble the order to prevent direct matching

Context:"""
