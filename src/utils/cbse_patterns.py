"""
CBSE Question Paper Pattern Configuration
Defines standard CBSE patterns for different subjects and classes
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SectionPattern:
    """Represents a section in CBSE question paper"""
    name: str
    questions: int
    marks_per_question: int
    total_marks: int
    description: str


@dataclass
class CBSEPattern:
    """Complete CBSE question paper pattern"""
    subject: str
    class_num: int
    total_marks: int
    time_limit: int  # in minutes
    sections: List[SectionPattern]


def get_cbse_pattern(subject: str, class_num: int) -> Optional[CBSEPattern]:
    """
    Get CBSE pattern for a specific subject and class.
    
    Args:
        subject: Subject name (e.g., 'Physics', 'Chemistry', 'Mathematics')
        class_num: Class number (e.g., 9, 10, 11, 12)
    
    Returns:
        CBSEPattern object or None if pattern not found
    """
    # Normalize subject name
    subject = subject.strip().lower()
    
    # Class 9-10 patterns
    if class_num in [9, 10]:
        if subject in ['science', 'physics', 'chemistry', 'biology']:
            return CBSEPattern(
                subject=subject.title(),
                class_num=class_num,
                total_marks=80,
                time_limit=180,  # 3 hours
                sections=[
                    SectionPattern(
                        name="Section A: MCQs & Assertion-Reason",
                        questions=20,
                        marks_per_question=1,
                        total_marks=20,
                        description="Multiple Choice Questions and Assertion-Reason type questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=6,
                        marks_per_question=2,
                        total_marks=12,
                        description="Questions requiring brief answers"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=6,
                        marks_per_question=3,
                        total_marks=18,
                        description="Questions requiring detailed explanations"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=5,
                        marks_per_question=5,
                        total_marks=25,
                        description="Questions requiring comprehensive answers with diagrams/derivations"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=3,
                        marks_per_question=5,
                        total_marks=15,
                        description="Case study based questions with sub-parts (1+1+3 or 2+3)"
                    )
                ]
            )
        
        elif subject in ['mathematics', 'maths', 'math']:
            return CBSEPattern(
                subject='Mathematics',
                class_num=class_num,
                total_marks=80,
                time_limit=180,
                sections=[
                    SectionPattern(
                        name="Section A: MCQs",
                        questions=20,
                        marks_per_question=1,
                        total_marks=20,
                        description="Multiple Choice Questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=5,
                        marks_per_question=2,
                        total_marks=10,
                        description="Questions requiring brief calculations"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=6,
                        marks_per_question=3,
                        total_marks=18,
                        description="Questions requiring detailed solutions"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=4,
                        marks_per_question=5,
                        total_marks=20,
                        description="Questions requiring comprehensive solutions with steps"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=3,
                        marks_per_question=4,
                        total_marks=12,
                        description="Case study based questions with sub-parts"
                    )
                ]
            )
    
    # Class 11-12 patterns
    elif class_num in [11, 12]:
        if subject in ['physics']:
            return CBSEPattern(
                subject='Physics',
                class_num=class_num,
                total_marks=70,
                time_limit=180,
                sections=[
                    SectionPattern(
                        name="Section A: MCQs",
                        questions=18,
                        marks_per_question=1,
                        total_marks=18,
                        description="Multiple Choice Questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=5,
                        marks_per_question=2,
                        total_marks=10,
                        description="Questions requiring brief answers"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=7,
                        marks_per_question=3,
                        total_marks=21,
                        description="Questions requiring detailed explanations"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=3,
                        marks_per_question=5,
                        total_marks=15,
                        description="Questions requiring comprehensive answers with derivations"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=2,
                        marks_per_question=3,
                        total_marks=6,
                        description="Case study based questions"
                    )
                ]
            )
        
        elif subject in ['chemistry']:
            return CBSEPattern(
                subject='Chemistry',
                class_num=class_num,
                total_marks=70,
                time_limit=180,
                sections=[
                    SectionPattern(
                        name="Section A: MCQs",
                        questions=18,
                        marks_per_question=1,
                        total_marks=18,
                        description="Multiple Choice Questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=5,
                        marks_per_question=2,
                        total_marks=10,
                        description="Questions requiring brief answers"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=7,
                        marks_per_question=3,
                        total_marks=21,
                        description="Questions requiring detailed explanations"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=3,
                        marks_per_question=5,
                        total_marks=15,
                        description="Questions requiring comprehensive answers"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=2,
                        marks_per_question=3,
                        total_marks=6,
                        description="Case study based questions"
                    )
                ]
            )
        
        elif subject in ['mathematics', 'maths', 'math']:
            return CBSEPattern(
                subject='Mathematics',
                class_num=class_num,
                total_marks=80,
                time_limit=180,
                sections=[
                    SectionPattern(
                        name="Section A: MCQs",
                        questions=20,
                        marks_per_question=1,
                        total_marks=20,
                        description="Multiple Choice Questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=5,
                        marks_per_question=2,
                        total_marks=10,
                        description="Questions requiring brief calculations"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=6,
                        marks_per_question=3,
                        total_marks=18,
                        description="Questions requiring detailed solutions"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=4,
                        marks_per_question=5,
                        total_marks=20,
                        description="Questions requiring comprehensive solutions"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=3,
                        marks_per_question=4,
                        total_marks=12,
                        description="Case study based questions"
                    )
                ]
            )
        
        elif subject in ['biology']:
            return CBSEPattern(
                subject='Biology',
                class_num=class_num,
                total_marks=70,
                time_limit=180,
                sections=[
                    SectionPattern(
                        name="Section A: MCQs",
                        questions=18,
                        marks_per_question=1,
                        total_marks=18,
                        description="Multiple Choice Questions"
                    ),
                    SectionPattern(
                        name="Section B: Very Short Answer Questions",
                        questions=5,
                        marks_per_question=2,
                        total_marks=10,
                        description="Questions requiring brief answers"
                    ),
                    SectionPattern(
                        name="Section C: Short Answer Questions",
                        questions=7,
                        marks_per_question=3,
                        total_marks=21,
                        description="Questions requiring detailed explanations"
                    ),
                    SectionPattern(
                        name="Section D: Long Answer Questions",
                        questions=3,
                        marks_per_question=5,
                        total_marks=15,
                        description="Questions requiring comprehensive answers"
                    ),
                    SectionPattern(
                        name="Section E: Case Study Based Questions",
                        questions=2,
                        marks_per_question=3,
                        total_marks=6,
                        description="Case study based questions"
                    )
                ]
            )
    
    # Pattern not found
    return None
