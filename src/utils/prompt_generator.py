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
        user_prompt: Optional custom prompt from user for partial override
    
    Returns:
        Generated prompt string or None if pattern not found
    """
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
    5. For MCQs, provide 4 options
    6. Return ONLY valid JSON, no additional text
    7. Do NOT INCLUDE the correct answer or solution in the output at anycost.
    8. CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.
    
    **SPECIAL INSTRUCTIONS FOR CASE STUDY QUESTIONS:**
    - Each case study passage MUST be substantial and educational
    - Passage length: MINIMUM 100-150 words (4-6 sentences)
    - The passage should present a real-world scenario, scientific phenomenon, or contextual information
    - Include specific facts, data, or examples that can be analyzed
    - Make the passage engaging and relevant to the topic
    - The passage should contain enough information to answer all sub-questions
    
    **SPECIAL INSTRUCTIONS FOR "READ THE PASSAGE AND ANSWER" QUESTIONS:**
    - This section should have ONE comprehensive passage (150-200 words)
    - Multiple questions (4-6 questions) should be based on this SINGLE passage
    - DO NOT create separate passages for each question
    - The passage should be rich enough to support all the questions
    - Questions should test comprehension, inference, and analysis of the SAME passage

    **REQUIRED JSON FORMAT:**
    {{
      "questionPaper": {{
        "title": "Class {class_num} {subject} Question Paper",
        "totalMarks": {cbse_pattern.total_marks},
        "duration": {cbse_pattern.time_limit},
        "mcq": [
          {{
            "questionNumber": 1,
            "question": "question text here",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "marks": 1
          }}
        ],
        "assertionReason": [
          {{
            "questionNumber": 2,
            "assertion": "assertion statement here",
            "reason": "reason statement here",
            "options": [
              "A) Both assertion and reason are true and reason is the correct explanation",
              "B) Both assertion and reason are true but reason is not the correct explanation",
              "C) Assertion is true but reason is false",
              "D) Both assertion and reason are false"
            ],
            "marks": 1
          }}
        ],
        "shortAnswer": [
          {{
            "questionNumber": 3,
            "question": "question text here",
            "marks": 2
          }}
        ],
        "longAnswer": [
          {{
            "questionNumber": 4,
            "question": "question text here",
            "marks": 5
          }}
        ],
        "caseStudy": [
          {{
            "questionNumber": 5,
            "passage": "Write a detailed case study passage here (100-150 words minimum). The passage should present a real-world scenario related to the topic. Include specific examples, data, or phenomena that students need to analyze. For example: 'In a recent study on plant growth, researchers observed that certain plants showed enhanced growth rates when exposed to specific wavelengths of light. The experiment involved growing identical seedlings under different light conditions - natural sunlight, red LED lights, blue LED lights, and a combination of both. After 30 days, plants under blue light showed 40% more leaf growth, while those under red light developed stronger root systems. The control group under natural sunlight showed balanced growth across all parameters.' This passage provides enough context and information for students to answer analytical questions.",
            "questions": [
              {{
                "subQuestionNumber": "5.1",
                "question": "sub-question text here",
                "marks": 1
              }}
            ],
            "marks": 4
          }}
        ],
        "readThePassageAndAnswer": [
          {{
            "questionNumber": 6,
            "passage": "IMPORTANT: Write ONE comprehensive passage here (150-200 words). ALL questions below should be based on THIS SAME passage. Example: 'The young seagull stood alone on his ledge, watching his family soar through the sky. His two brothers and sister had flown away the day before, leaving him behind. He wanted to fly like them, but when he looked down at the vast green sea far below, fear gripped his heart. His mother and father circled around, calling to him, encouraging him to take the leap. He tried running forward and flapping his wings, but each time he reached the edge, he stopped. His legs wouldn't move forward. The drop was too scary. Hours passed, and hunger began to gnaw at him. He saw his mother flying towards him with a piece of fish in her beak. She came close but stopped just out of reach, holding the fish tantalizingly before him. He leaned out eagerly, trying to reach it, forgetting his fear in his hunger. Suddenly, he felt himself falling, tumbling through the air. But then, instinctively, he spread his wings and felt them catch the wind. He was flying! The sea no longer seemed scary but beautiful.'",
            "questions": [
              {{
                "subQuestionNumber": "6.1",
                "question": "What was the seagull's main fear?",
               "marks": 2
              }},
              {{
                "subQuestionNumber": "6.2",
                "question": "How did the mother seagull help him overcome his fear?",
                "marks": 2
              }},
              {{
                "subQuestionNumber": "6.3",
                "question": "What made the seagull finally take the leap?",
                "marks": 2
              }},
              {{
                "subQuestionNumber": "6.4",
                "question": "What does this story teach us about overcoming fears?",
                "marks": 2
              }}
            ],
            "marks": 8
          }}
        ]
      }}
    }}

    Note: Include only the question types that are part of your question paper based on the section structure. If a section doesn't apply, omit that key from the JSON.

    CRITICAL : Generate the complete question paper in JSON format STRICTLY following the above format:"""

def generate_general_prompt(
      board: str,
      class_num: int,
      subject: str,
      topics: List[str],
      difficulty: str,
      question_count: int,
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
        user_prompt: Optional custom prompt from user for partial override
    
    Returns:
        Generated prompt string
    """
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

      CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.

      **REQUIRED JSON FORMAT:**
      {{
        "questionPaper": {{
          "title": "Class {class_num} {subject} Question Paper",
          "totalQuestions": {question_count},
          "difficulty": "{difficulty}",
          "wordProblems": [
            {{
              "questionNumber": 1,
              "question": "question text here",
              "marks": 2
            }}
          ],
          "mcq": [
            {{
              "questionNumber": 2,
              "question": "question text here",
              "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
              "marks": 1
            }}
          ],
          "fillInTheBlanks": [
            {{
              "questionNumber": 3,
              "question": "question text with _____ blank",
              "marks": 1
            }}
          ],
          "trueOrFalse": [
            {{
              "questionNumber": 4,
              "statement": "statement here",
              "marks": 1
            }}
          ],
          "matchTheFollowing": [
            {{
              "questionNumber": 5,
              "columnA": ["Item 1", "Item 2", "Item 3"],
              "columnB": ["Match 2", "Match 1", "Match 3"],
              "marks": 2
            }}
          ],
          "storyBasedProblems": [
            {{
              "questionNumber": 6,
              "story": "story context here",
              "question": "question based on story",
              "marks": 3
            }}
          ]
        }}
      }}

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

        **SPECIAL INSTRUCTIONS FOR COMPREHENSIVE QUESTIONS:**
        - The paragraph MUST be substantial: MINIMUM 100-120 words (5-7 sentences)
        - Use proper grammar and varied sentence structures
        - The paragraph should contain multiple grammatical elements for analysis
        - Include different parts of speech, tenses, and sentence types
        - Make it engaging and age-appropriate for Class {class_num}

        CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.

        **REQUIRED JSON FORMAT:**
        {{
        "questionPaper": {{
            "title": "Class {class_num} {subject} Question Paper",
            "totalQuestions": {question_count},
            "difficulty": "{difficulty}",
            "comprehensiveQuestions": [
            {{
                "questionNumber": 1,
                "paragraph": "Write a detailed paragraph here (100-120 words minimum). The paragraph should contain diverse grammatical elements for students to analyze. Example: 'Sarah woke up early on Saturday morning, feeling excited about her upcoming trip to the mountains. She had been planning this adventure for months, carefully selecting her equipment and studying the trail maps. Her younger brother, Tom, who usually loved outdoor activities, was surprisingly reluctant to join her this time. \"I have already committed to helping Dad with the garden,\" he explained apologetically. Sarah understood his decision and proceeded with her preparations independently. By noon, she had packed her backpack, checked the weather forecast, and informed her parents about her itinerary. The journey would be challenging, but she felt confident and well-prepared.' Use this as a reference for creating engaging, grammatically rich paragraphs.",
                "questions": [
                {{
                    "subQuestionNumber": "1.1",
                    "question": "question based on paragraph",
                    "marks": 2
                }}
                ]
            }}
            ],
            "mcq": [
            {{
                "questionNumber": 2,
                "question": "question text here",
                "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                "marks": 1
            }}
            ],
            "fillInTheBlanks": [
            {{
                "questionNumber": 3,
                "question": "question text with _____ blank",
                "marks": 1
            }}
            ],
            "trueOrFalse": [
            {{
                "questionNumber": 4,
                "statement": "statement here",
                "marks": 1
            }}
            ],
            "matchTheFollowing": [
            {{
                "questionNumber": 5,
                "columnA": ["Item 1", "Item 2", "Item 3"],
                "columnB": ["Match 2", "Match 1", "Match 3"],
                "marks": 2
            }}
            ],
            "wordMeaning": [
            {{
                "questionNumber": 6,
                "word": "word here",
                "marks": 1
            }}
            ]
        }}
        }}

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
            
            **IMPORTANT**: The paragraph MUST be 100-120 words minimum (5-7 sentences in Hindi). Create an engaging paragraph in Hindi with diverse grammatical elements for analysis.
            
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

          CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}. Question Paper should be in Hindi language.

          **REQUIRED JSON FORMAT:**
          {{
            "questionPaper": {{
              "title": "Class {class_num} {subject} Question Paper",
              "totalQuestions": {question_count},
              "difficulty": "{difficulty}",
              "descriptiveQuestions": [
                {{
                  "questionNumber": 1,
                  "question": "प्रश्न यहाँ",
                  "marks": 3
                }}
              ],
              "mcq": [
                {{
                  "questionNumber": 2,
                  "question": "प्रश्न यहाँ",
                  "options": ["A) विकल्प1", "B) विकल्प2", "C) विकल्प3", "D) विकल्प4"],
                  "marks": 1
                }}
              ],
              "fillInTheBlanks": [
                {{
                  "questionNumber": 3,
                  "question": "_____ के साथ प्रश्न",
                  "marks": 1
                }}
              ],
              "trueOrFalse": [
                {{
                  "questionNumber": 4,
                  "statement": "कथन यहाँ",
                  "marks": 1
                }}
              ],
              "matchTheFollowing": [
                {{
                  "questionNumber": 5,
                  "columnA": ["आइटम 1", "आइटम 2"],
                  "columnB": ["मिलान 2", "मिलान 1"],
                  "marks": 2
                }}
              ],
              "wordMeaning": [
                {{
                  "questionNumber": 6,
                  "word": "शब्द",
                  "marks": 1
                }}
              ]
            }}
          }}

          Context:
          """
    
    # Default/General subjects (including English)
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

          CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.

          **REQUIRED JSON FORMAT:**
          {{
            "questionPaper": {{
              "title": "Class {class_num} {subject} Question Paper",
              "totalQuestions": {question_count},
              "difficulty": "{difficulty}",
              "descriptiveQuestions": [
                {{
                  "questionNumber": 1,
                  "question": "question text here",
                  "marks": 5
                }}
              ],
              "mcq": [
                {{
                  "questionNumber": 2,
                  "question": "question text here",
                  "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                  "marks": 1
                }}
              ],
              "fillInTheBlanks": [
                {{
                  "questionNumber": 3,
                  "question": "question text with _____ blank",
                  "marks": 1
                }}
              ],
              "trueOrFalse": [
                {{
                  "questionNumber": 4,
                  "statement": "statement here",
                  "marks": 1
                }}
              ],
              "matchTheFollowing": [
                {{
                  "questionNumber": 5,
                  "columnA": ["Item 1", "Item 2", "Item 3"],
                  "columnB": ["Match 2", "Match 1", "Match 3"],
                  "marks": 2
                }}
              ],
              "shortAnswer": [
                {{
                  "questionNumber": 6,
                  "question": "question text here",
                  "marks": 2
                }}
              ]
            }}
          }}

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
        content: Content to summarize
    
    Returns:
        Generated prompt string
    """
    return f"""You are an expert educational content summarizer specializing in creating concise chapter summaries for students. Create a comprehensive yet concise summary of the following content.

    Details:
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}

    Instructions:
    1. Create a well-structured chapter summary suitable for Class {class_num} students
    2. Include all key concepts, definitions, and important points
    3. Organize the summary with clear headings and subheadings
    4. Use bullet points for listing important facts or steps
    5. Highlight formulas, dates, names, or critical information
    6. Keep the language clear and appropriate for the student's level
    7. Include a brief conclusion or key takeaways section
    8. Make it comprehensive but concise - aim for clarity over length

    Format the summary with:
    - Clear section headings (use ** for bold)
    - Bullet points for key points (use • or -)
    - Numbered lists for sequential information
    - Proper spacing for readability

    Content to summarize:
    {content}

    Generate a well-formatted chapter summary:
    """

def generate_flashcard_prompt(
      board: str,
      class_num: str,
      subject: str,
      topics: List[str],
      content: str,
      card_count: int = 20
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
    return f"""You are an expert educational content creator specializing in creating flashcards for students. Create engaging and educational flashcards based on the provided content.

    Details:
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}
    - Number of Cards: {card_count}

    Instructions:
    1. Create {card_count} flashcards from the provided content
    2. Each flashcard should have a clear FRONT (question/prompt) and BACK (answer/explanation)
    3. Make questions age-appropriate for Class {class_num}
    4. Cover different aspects of the topics: definitions, examples, applications, facts
    5. Use varied question types: What is...?, Why does...?, How does...?, When did...?, etc.
    6. Keep answers concise but informative
    7. Include the topic name for each card

    Format your response as a JSON array with this exact structure:
    [
      {{
        "front": "Question or prompt here",
        "back": "Answer or explanation here",
        "topic": "Topic name here"
      }}
    ]

    Content to create flashcards from:
    {content}

    Generate the flashcards in JSON format:
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
    return f"""You are an expert educational content creator specializing in creating mind maps and flowcharts for students. Create a comprehensive mind map structure for quick revision.

    Details:
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}

    Instructions:
    1. Create a hierarchical mind map structure with main topics, subtopics, and key points
    2. Make it suitable for Class {class_num} students for quick revision
    3. Include important concepts, definitions, examples, and relationships
    4. Use clear, concise labels that are easy to understand
    5. Organize information in a logical flow from general to specific
    6. Include 3-4 main branches with 2-4 sub-branches each
    7. Add key facts, formulas, or important points as leaf nodes

    Format your response as a JSON object with this exact structure:
    {{
      "title": "Main topic title here",
      "nodes": [
        {{
          "id": "unique_id_here",
          "label": "Node label here",
          "type": "main|branch|leaf",
          "children": ["child_id_1", "child_id_2"],
          "color": "color_code_here"
        }}
      ],
      "connections": [
        {{
          "from": "parent_id",
          "to": "child_id"
        }}
      ]
    }}

    Content to create mind map from:
    {content}

    Generate the mind map structure in JSON format:
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
    return f"""You are an expert educational content creator specializing in memory techniques, mnemonics, and study tricks. Create engaging and memorable study tricks and mnemonics for the following content.

    Details:
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}

    Instructions:
    1. Create clever mnemonics, acronyms, and memory tricks for key concepts
    2. Use rhymes, stories, or visual associations to make information memorable
    3. Include tricks for formulas, definitions, dates, names, and important facts
    4. Make each trick fun, creative, and easy to remember
    5. Use age-appropriate language for Class {class_num} students
    6. Provide explanation for why each trick works
    7. Include both general study tips and topic-specific memory techniques
    8. Add practical examples of how to apply each trick

    Format each trick as:
    ### [Catchy Title for the Trick]
    - What it helps remember
    - The mnemonic/trick itself
    - Why it works
    - Example or practice tip

    Generate at least 5-10 different study tricks and mnemonics covering different aspects of the content.

    Content to analyze:
    {content}

    Generate creative and memorable study tricks:
    """

def generate_answer_prompt(
      board: str,
      class_num: int,
      subject: str,
      topics: List[str],
      questions: dict,
      content: str,
      use_cbse_pattern: bool = False
  ) -> str:
    """
    Generate prompt for answer key generation based on question paper.
    
    Args:
        board: Educational board
        class_num: Class number
        subject: Subject name
        topics: List of topic names
        questions: Question paper JSON object
        content: Educational content from textbook
        use_cbse_pattern: Whether the questions follow CBSE pattern
    
    Returns:
        Generated prompt string for answer generation
    """
    # Convert questions dict to formatted string for better readability
    import json
    questions_text = json.dumps(questions, indent=2)
    
    if use_cbse_pattern:
        return f"""You are an experienced CBSE teacher creating comprehensive answer keys.

    Generate detailed answers for this question paper following CBSE marking scheme format.

    **Subject Details:**
    - Board: {board}
    - Class: {class_num}
    - Subject: {subject}
    - Topics: {', '.join(topics)}

    **Question Paper (JSON):**
    {questions_text}

    **Educational Content (for reference):**
    {content[:8000]}

    CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.

    **REQUIRED JSON FORMAT:**
    {{
      "answerKey": {{
        "mcq": [
          {{
            "questionNumber": 1,
            "correctAnswer": "C",
            "explanation": "Detailed explanation here",
            "marks": 1
          }}
        ],
        "assertionReason": [
          {{
            "questionNumber": 2,
            "correctAnswer": "A",
            "explanation": "Detailed explanation here",
            "marks": 1
          }}
        ],
        "shortAnswer": [
          {{
            "questionNumber": 3,
            "answer": "Detailed answer with step-by-step solution",
            "keyPoints": ["Point 1", "Point 2"],
            "marks": 2
          }}
        ],
        "longAnswer": [
          {{
            "questionNumber": 4,
            "answer": "Comprehensive answer with detailed explanation",
            "keyPoints": ["Main point 1", "Main point 2", "Main point 3"],
            "marks": 5
          }}
        ],
        "caseStudy": [
          {{
            "questionNumber": 5,
            "subQuestions": [
              {{
                "subQuestionNumber": "5.1",
                "answer": "Answer here",
                "marks": 1
              }}
            ]
          }}
        ]
      }}
    }}

    **Instructions:**
    - Provide step-by-step solutions for all questions
    - For MCQs, provide the correct answer option and explain why it's correct
    - For descriptive questions, provide comprehensive explanations with proper formatting
    - Follow CBSE marking scheme guidelines
    - Include all key points that would earn marks
    - Be pedagogically sound and educational
    - Only include answer sections for question types that exist in the question paper"""

    else:
        # General answer format for non-CBSE patterns
        return f"""You are an experienced teacher creating comprehensive answer keys.

      Generate detailed answers for this question paper.

      **Subject Details:**
      - Board: {board}
      - Class: {class_num}
      - Subject: {subject}
      - Topics: {', '.join(topics)}

      **Question Paper (JSON):**
      {questions_text}

      **Educational Content (for reference):**
      {content[:8000]}

      CRITICAL: You MUST respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or explanations. Start your response with {{ and end with }}.

      **REQUIRED JSON FORMAT:**
      {{
        "answerKey": {{
          "descriptiveQuestions": [
            {{
              "questionNumber": 1,
              "answer": "Detailed answer here",
              "keyPoints": ["Point 1", "Point 2"],
              "marks": 5
            }}
          ],
          "mcq": [
            {{
              "questionNumber": 2,
              "correctAnswer": "B",
              "explanation": "Explanation why this is correct",
              "marks": 1
            }}
          ],
          "fillInTheBlanks": [
            {{
              "questionNumber": 3,
              "answer": "correct word/phrase",
              "marks": 1
            }}
          ],
          "trueOrFalse": [
            {{
              "questionNumber": 4,
              "correctAnswer": "True",
              "explanation": "Brief explanation",
              "marks": 1
            }}
          ],
          "matchTheFollowing": [
            {{
              "questionNumber": 5,
              "correctMatches": {{
                "Item 1": "Match 1",
                "Item 2": "Match 2",
                "Item 3": "Match 3"
              }},
              "marks": 2
            }}
          ],
          "shortAnswer": [
            {{
              "questionNumber": 6,
              "answer": "Concise answer here",
              "keyPoints": ["Point 1", "Point 2"],
              "marks": 2
            }}
          ],
          "wordProblems": [
            {{
              "questionNumber": 7,
              "solution": "Step-by-step solution",
              "steps": ["Step 1", "Step 2", "Final answer"],
              "marks": 2
            }}
          ],
          "storyBasedProblems": [
            {{
              "questionNumber": 8,
              "solution": "Step-by-step solution",
              "steps": ["Extract data", "Apply formula", "Calculate", "Final answer"],
              "marks": 3
            }}
          ],
          "comprehensiveQuestions": [
            {{
              "questionNumber": 9,
              "subQuestions": [
                {{
                  "subQuestionNumber": "9.1",
                  "answer": "Answer here",
                  "marks": 2
                }}
              ]
            }}
          ],
          "wordMeaning": [
            {{
              "questionNumber": 10,
              "word": "vocabulary word",
              "meaning": "definition or meaning",
              "marks": 1
            }}
          ]
        }}
      }}

      **Instructions:**
      - Provide detailed, accurate answers for each question
      - For MCQs, provide the correct answer option and explain why
      - For descriptive questions, provide comprehensive explanations
      - For word problems and story-based problems, show step-by-step solutions
      - Use clear formatting and include all key points
      - Be pedagogically sound and educational
      - Only include answer sections for question types that exist in the question paper"""

def generate_chat_prompt(
      board: str,
      class_num: str,
      subject: str,
      topics: List[str],
      message: str,
      conversation_history: List[dict],
      content: Optional[str] = None
  ) -> str:
    """
    Generate prompt for AI tutor chat conversation.
    
    Args:
        board: Educational board (e.g., 'CBSE')
        class_num: Class number (e.g., '10')
        subject: Subject name (e.g., 'Science')
        topics: List of topic names
        message: Current user message
        conversation_history: List of previous messages with role and content
        content: Optional textbook content for reference
    
    Returns:
        Generated prompt string for chat conversation
    """
    # Build system prompt with educational context
    system_prompt = f"""You are a friendly, knowledgeable AI tutor assistant specialized in helping students with their studies. You provide clear, encouraging, and educational responses.

      Your current student context:
      - Board: {board}
      - Class: {class_num}
      - Subject: {subject}
      - Topics: {', '.join(topics)}

      Guidelines:
      - Be patient, supportive, and encouraging
      - Explain concepts in age-appropriate language for Class {class_num} students
      - Provide examples when helpful
      - Ask follow-up questions to ensure understanding
      - Keep responses concise but thorough
      - Use emojis occasionally to keep it friendly 😊
      - Focus on the provided topics and subject matter
      - If asked about topics outside the current context, gently redirect to academic help in {subject}
      - Use the conversation history to maintain context and provide personalized assistance
      - Ground your explanations in the curriculum appropriate for {board} Class {class_num}"""

    # Add content reference if provided
    if content:
        system_prompt += f"""

        **Reference Content from Textbook:**
        Use the following educational content to provide accurate, curriculum-aligned responses:

        {content}

        IMPORTANT: Base your explanations on this textbook content when relevant. This ensures your responses align with what the student is learning in class."""

    # Format conversation history
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\n**Previous Conversation:**\n"
        for msg in conversation_history[-10:]:  # Last 10 messages to avoid token limits
            role = msg.get('role', 'unknown')
            msg_content = msg.get('content', '')
            if role == 'user':
                conversation_context += f"Student: {msg_content}\n"
            elif role == 'assistant':
                conversation_context += f"You: {msg_content}\n"
    
    # Build the complete prompt
    full_prompt = f"""{system_prompt}{conversation_context}

      **Current Student Question:**
      {message}

      **Your Response:**
      Provide a helpful, educational response that addresses the student's question. Remember to be encouraging and supportive!"""

    return full_prompt

