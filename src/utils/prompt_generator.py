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
    questions_text: Optional[str] = None,
    user_prompt: Optional[str] = None
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
    
    # Build custom prompt section if provided
    custom_instructions = ""
    if user_prompt:
        custom_instructions = f"""

**USER'S CUSTOM REQUIREMENTS (FOLLOW STRICTLY):**
{user_prompt}

IMPORTANT: The user has provided custom requirements above. Follow them STRICTLY.
- If the user specifies a particular number of questions for a section (e.g., "10 MCQs"), generate EXACTLY that number, overriding the default pattern.
- For sections NOT mentioned in the user's custom requirements, follow the default CBSE pattern structure provided above.
- This is a PARTIAL OVERRIDE - only modify what the user explicitly requests.
"""
    
    return f"""You are an experienced CBSE teacher creating a question paper for Class {class_num} {subject}.

**Exam Pattern Details:**
- Total Marks: {cbse_pattern.total_marks}
- Time: {cbse_pattern.time_limit} minutes
- Board: {board}
- Topics: {', '.join(topics)}

**Section Structure:**
{sections_description}{custom_instructions}

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
    questions_text: Optional[str] = None,
    user_prompt: Optional[str] = None
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
        user_prompt: Optional custom prompt from user for partial override
    
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
    
    # Build custom prompt section if provided
    custom_instructions = ""
    if user_prompt:
        custom_instructions = f"""

**USER'S CUSTOM REQUIREMENTS (FOLLOW STRICTLY):**
{user_prompt}

IMPORTANT: The user has provided custom requirements above. Follow them STRICTLY.
- If the user specifies a particular number/type of questions (e.g., "10 MCQs, 5 fill in the blanks"), generate EXACTLY that, overriding the default structure.
- For question types NOT mentioned in the user's requirements, follow the default structure provided above.
- This is a PARTIAL OVERRIDE - only modify what the user explicitly requests.
"""
    
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
            6. Story-Based Problems ({question_count - 5 * (question_count // 6)} questions): Provide a story from which students must extract data to solve a mathematical problem. These problems should be engaging and contextually relevant.{custom_instructions}

            Context:
        """
    
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
            6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Ask for the meanings of words used in the chapter.{custom_instructions}

            Context:
        """
    
    # Hindi / Hindi Grammar
    elif subject_lower in ['hindi', 'hindi grammar']:
        if subject_lower == 'hindi':
            structure = f"""1. Descriptive Questions ({question_count // 6} questions): Questions that require detailed explanations
                2. MCQ Questions ({question_count // 6} questions): Multiple-choice questions with one correct answer out of four options.
                3. Fill in the Blanks ({question_count // 6} questions): Statements with missing words to be filled based on the chapter.
                4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
                5. Match the Following ({question_count // 6} questions): Pairs of related items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
                6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Questions asking for the meaning of words used in the chapter.

                Question Paper should be in Hindi language and start directly with descriptive questions without providing any instructions.
            """
        else:
            structure = f"""1. Comprehensive Questions ({question_count // 6} questions): Provide one paragraph only and ask grammatical questions related to it.
            2. MCQ Questions ({question_count // 6} questions): Multiple-choice questions with one correct answer out of four options.
            3. Fill in the Blanks ({question_count // 6} questions): Statements with missing words to be filled based on the chapter.
            4. True or False ({question_count // 6} questions): Statements that need to be marked as true or false.
            5. Match the Following ({question_count // 6} questions): Pairs of related items to be matched correctly. Ensure that the order of items in both columns is jumbled to prevent direct matching.
            6. Word Meaning ({question_count - 5 * (question_count // 6)} questions): Questions asking for the meaning of words used in the chapter.

            Question Paper should be in Hindi language and start directly with descriptive questions without providing any instructions.        """
                    
        return f"""You are an intelligent and experienced teacher with a deep understanding of the provided topics and context. Your task is to create a comprehensive question paper based on the details such as class, subject, and topics provided to you. Follow the context strictly and ensure the questions reflect the topics accurately without adding any personal interpretations.

            Details:
            - Board: {board}
            - Class: {class_num}
            - Subject: {subject}
            - Topics: {', '.join(topics)}
            - Difficulty Level: {difficulty}
            - Total Questions: {question_count}

            Structure the question paper as follows:
            {structure}{custom_instructions}

            Context:
        """
    
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
        6. **Short Answer Questions** ({question_count - 5 * (question_count // 6)} questions): Brief explanations required{custom_instructions}

        Requirements:
        - Ensure questions are age-appropriate for Class {class_num}
        - Maintain {difficulty.lower()} difficulty level throughout
        - Focus strictly on the provided topics: {', '.join(topics)}
        - Use clear, unambiguous language
        - For MCQs, ensure only one option is clearly correct
        - For Match the Following, scramble the order to prevent direct matching

        Context:
    """

def generate_summary_prompt(
        board: str,
        class_num: str,
        subject: str,
        topics: List[str],
        content: str
    ) -> str:
    """
    Generate prompt for chapter summarization.
    
    Args:
        board: Educational board
        class_num: Class number
        subject: Subject name
        topics: List of topic names
        content: Chapter content to summarize
    
    Returns:
        Generated prompt string
    """
    return f"""You are an expert teacher creating a comprehensive chapter summary for students.

        Details:
        - Board: {board}
        - Class: {class_num}
        - Subject: {subject}
        - Topics: {', '.join(topics)}

        Task:
        Create a detailed, well-structured summary of the provided content. The summary should be easy to understand and perfect for exam revision.

        Format your response using Markdown with the following structure:
        # [Chapter/Topic Name]

        ## Key Concepts
        [Explain the core concepts clearly]

        ## Important Definitions
        - **[Term]**: [Definition]

        ## Key Formulas/Points (if applicable)
        - [Point 1]
        - [Point 2]

        ## Summary
        [Detailed paragraph summary of the chapter]

        ## Exam Tips
        - [Tip 1]
        - [Tip 2]

        Content to Summarize:
        {content}

        Generate the summary in Markdown format:
    """


def generate_flashcard_prompt(
    board: str,
    class_num: str,
    subject: str,
    topics: List[str],
    content: str,
    card_count: int = 15
) -> str:
    """
    Generate prompt for flashcard generation.
    
    Args:
        board: Educational board
        class_num: Class number
        subject: Subject name
        topics: List of topic names
        content: Content to generate flashcards from
        card_count: Number of flashcards to generate
    
    Returns:
        Generated prompt string
    """
    return f"""You are an expert teacher creating study flashcards for students.

    Details:
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}
    - Number of Cards: {card_count}

    Task:
    Create {card_count} high-quality flashcards based on the provided content.
    - Front: A clear, concise question or concept.
    - Back: A comprehensive but concise answer or explanation.
    - Topic: The specific sub-topic this card belongs to.

    Content to use:
    {content}

    IMPORTANT: Return ONLY a valid JSON array of objects. No markdown formatting, no code blocks.
    
    Required JSON Structure:
    [
      {{
        "id": "1",
        "front": "Question or concept here",
        "back": "Answer or explanation here",
        "topic": "Specific sub-topic"
      }}
    ]
    """

def generate_mindmap_prompt(
        board: str,
        class_num: str,
        subject: str,
        topics: List[str],
        content: str
    ) -> str:
    """
    Generate prompt for mind map generation.
    
    Args:
        board: Educational board
        class_num: Class number
        subject: Subject name
        topics: List of topic names
        content: Content to generate mind map from
    
    Returns:
        Generated prompt string
    """
    return f"""You are an expert teacher creating a mind map for students to revise concepts.

        Details:
        - Board: {board}
        - Class: {class_num}
        - Subject: {subject}
        - Topics: {', '.join(topics)}

        Task:
        Create a hierarchical mind map structure based on the provided content.
        - The root node should be the main topic or subject.
        - Branch nodes should be major sub-topics.
        - Leaf nodes should be specific concepts or key points.

        Content to use:
        {content}

        IMPORTANT: Return ONLY a valid JSON object. No markdown formatting, no code blocks.
        
        Required JSON Structure:
        {{
        "title": "Main Title of Mind Map",
        "nodes": [
            {{ "id": "1", "label": "Main Topic", "type": "main" }},
            {{ "id": "2", "label": "Sub Topic 1", "type": "branch" }},
            {{ "id": "3", "label": "Concept A", "type": "leaf" }}
        ],
        "connections": [
            {{ "from": "1", "to": "2" }},
            {{ "from": "2", "to": "3" }}
        ]
        }}
        
        Ensure:
        1. All nodes have unique IDs.
        2. 'type' must be one of: 'main', 'branch', 'leaf'.
        3. All connections reference valid node IDs.
        4. The structure is logical and hierarchical.
    """

def generate_study_tricks_prompt(
        board: str,
        class_num: str,
        subject: str,
        topics: List[str],
        content: str
    ) -> str:
        """
        Generate prompt for study tricks and mnemonics generation.
        
        Args:
            board: Educational board
            class_num: Class number
            subject: Subject name
            topics: List of topic names
            content: Content to generate tricks from
        
        Returns:
            Generated prompt string
        """
        return f"""You are an expert teacher creating study tricks, mnemonics, and memory aids for students.

            Details:
            - Board: {board}
            - Class: {class_num}
            - Subject: {subject}
            - Topics: {', '.join(topics)}

            Task:
            Create creative and effective study tricks, mnemonics, and analogies to help students remember key concepts from the provided content.

            Content to use:
            {content}

            Output Format (Markdown):
            - Use '# Main Title' for the overall title.
            - Use '## Section Title' for grouping tricks by concept.
            - Use '### Trick Name' for individual tricks/mnemonics.
            - Use bullet points (* or -) for explanation steps.
            - Use numbered lists (1.) for sequential steps.
            - Be creative, funny, and memorable.
            - Include "Pro Tip" sections where applicable.

            Example Output Structure:
            # Mastering Chemical Reactions
            
            ## Types of Reactions
            
            ### The "C-D-D-S" Mnemonic
            * **C**ombination: Two become one (A+B -> AB)
            * **D**ecomposition: One becomes two (AB -> A+B)
            * **D**isplacement: The bully kicks out the weak (A+BC -> AC+B)
            * **D**ouble **D**isplacement: The partner swap (AB+CD -> AD+CB)
            
            ## Reactivity Series
            
            ### Please Stop Calling Me A Zebra...
            1. **P**otassium
            2. **S**odium
            3. **C**alcium
            ...
        """

