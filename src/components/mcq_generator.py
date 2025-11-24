"""
MCQ Generator Component
Handles MCQ generation using LLM
"""
from langchain_core.prompts import ChatPromptTemplate
import json
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class MCQGenerator:
    """Generates MCQs using LLM based on content and difficulty level."""
    
    def __init__(self, llm):
        """
        Initialize MCQ generator with LLM.
        
        Args:
            llm: Language model instance (e.g., ChatGroq)
        """
        self.llm = llm
    
    def generate_mcqs(self, num_questions, difficulty_level, topic, content):
        """
        Generate MCQs based on the chapter content.
        
        Args:
            num_questions (int): Number of MCQs to generate
            difficulty_level (str): 'easy', 'medium', or 'hard'
            topic (str): Topic name
            content (str): Content to generate questions from
        
        Returns:
            list: List of MCQ dictionaries or None if error
        """
        logger.info(f"Generating {num_questions} MCQs at {difficulty_level} difficulty for topic: {topic}")
        
        # Validate difficulty level
        if difficulty_level.lower() not in ['easy', 'medium', 'hard']:
            logger.error(f"Invalid difficulty level: {difficulty_level}")
            return None
        
        logger.debug(f"Content length: {len(content)} characters")
        
        # Escape curly braces in content to prevent f-string interpretation issues
        escaped_content = content.replace('{', '{{').replace('}', '}}')
        logger.debug("Content escaped for template processing")
        
        # Create MCQ generation prompt
        mcq_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert educational assessment creator specializing in Multiple Choice Questions (MCQs).\\n\\n"
             "## Your Task:\\n"
             f"Generate EXACTLY {num_questions} Multiple Choice Questions at **{difficulty_level.upper()} difficulty level** "
             "based STRICTLY on the provided chapter content.\\n\\n"
             "## Difficulty Level Guidelines:\\n"
             "### EASY:\\n"
             "- Test direct recall and basic understanding\\n"
             "- Questions about definitions, simple facts, and key terms\\n"
             "- Straightforward language\\n"
             "- Example: 'What is photosynthesis?'\\n\\n"
             "### MEDIUM:\\n"
             "- Test comprehension and application\\n"
             "- Questions requiring understanding of relationships and processes\\n"
             "- May involve simple analysis or comparison\\n"
             "- Example: 'How does photosynthesis differ from respiration?'\\n\\n"
             "### HARD:\\n"
             "- Test analysis, synthesis, and evaluation\\n"
             "- Questions requiring critical thinking and deeper understanding\\n"
             "- May involve problem-solving or application to new scenarios\\n"
             "- And try to implement such that the question will cover 2-3 topics."
             "- In case of maths, physics and chemistry set question such that it uses concept of 2-3 topics and "
             "set good quality questions."
             "- Example: 'What would happen to the rate of photosynthesis if CO2 levels decreased?'\\n\\n"
             "## MCQ Format Requirements:\\n"
             "1. Each question must have EXACTLY 4 options (A, B, C, D)\\n"
             "2. ONLY ONE option should be correct\\n"
             "3. Distractors (wrong options) should be plausible but clearly incorrect\\n"
             "4. Avoid 'All of the above' or 'None of the above' options\\n"
             "5. Options should be roughly similar in length\\n"
             "6. Questions must be clear, unambiguous, and grammatically correct\\n\\n"
             "7. Question can be numericals as well where it is needed."
             "## Output Format:\\n"
             "Return ONLY valid JSON (no markdown, no code blocks) in this exact structure:\\n"
             "{{\\n"
             '  "mcqs": [\\n'
             "    {{\\n"
             '      "question": "Question text here?",\\n'
             '      "options": {{\\n'
             '        "A": "Option A text",\\n'
             '        "B": "Option B text",\\n'
             '        "C": "Option C text",\\n'
             '        "D": "Option D text"\\n'
             "      }},\\n"
             '      "correct_answer": "A",\\n'
             '      "explanation": "Brief explanation why this answer is correct"\\n'
             "    }}\\n"
             "  ]\\n"
             "}}\\n\\n"
             "## Important Rules:\\n"
             "- Base ALL questions on the provided context only\\n"
             "- Do NOT create questions about information not in the context\\n"
             "- Ensure questions are diverse and cover different aspects of the chapter\\n"
             "- Maintain consistent difficulty level across all questions\\n"
             f"- Generate EXACTLY {num_questions} questions, no more, no less\\n\\n"
             "## Chapter Content:\\n"
             f"{escaped_content}"
            ),
            ("human", f"Generate {num_questions} {difficulty_level} level MCQs from the chapter content provided.")
        ])

        # Generate MCQs
        logger.info("Invoking LLM to generate MCQs...")
        chain = mcq_prompt | self.llm
        response = chain.invoke({})
        logger.debug("LLM response received")

        try:
            # Parse JSON response
            response_text = response.content.strip()
            
            # Find JSON content between ```json and ``` or just ``` and ```
            if "```" in response_text:
                # Extract content between first and last ``` 
                # This handles cases where there's text before the code block
                parts = response_text.split("```")
                # Usually the code block is the second part (index 1)
                # But sometimes there might be multiple, so we look for the one looking like JSON
                for part in parts:
                    clean_part = part.strip()
                    if clean_part.startswith("json"):
                        clean_part = clean_part[4:].strip()
                    
                    if clean_part.startswith("{") and clean_part.endswith("}"):
                        response_text = clean_part
                        break
            
            # If still not clean, try to find the first { and last }
            if not response_text.startswith("{"):
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    response_text = response_text[start_idx:end_idx+1]
                
            mcqs_data = json.loads(response_text)
            logger.info(f"Successfully generated {len(mcqs_data['mcqs'])} MCQs")
            return mcqs_data['mcqs']
        except Exception as e:
            logger.error(f"Error parsing MCQs: {e}")
            logger.debug(f"Raw response: {response.content}")
            return None
