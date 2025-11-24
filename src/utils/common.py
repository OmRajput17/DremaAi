"""
Utility functions for common operations
"""


def validate_difficulty_level(difficulty):
    """
    Validate difficulty level input.
    
    Args:
        difficulty (str): Difficulty level to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return difficulty.lower() in ['easy', 'medium', 'hard']


def validate_num_questions(num):
    """
    Validate number of questions.
    
    Args:
        num (int): Number of questions
    
    Returns:
        bool: True if valid (1-20), False otherwise
    """
    try:
        num = int(num)
        return 1 <= num <= 20
    except (ValueError, TypeError):
        return False


def format_topic_name(topic_num, topic_name=None):
    """
    Format topic name for display.
    
    Args:
        topic_num (str): Topic number
        topic_name (str, optional): Topic name
    
    Returns:
        str: Formatted topic name
    """
    if topic_name:
        return f"{topic_num}. {topic_name}"
    return f"Topic {topic_num}"


def clean_json_response(response_text):
    """
    Clean JSON response from LLM (remove markdown code blocks).
    
    Args:
        response_text (str): Raw response text
    
    Returns:
        str: Cleaned JSON string
    """
    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    return response_text.strip()
