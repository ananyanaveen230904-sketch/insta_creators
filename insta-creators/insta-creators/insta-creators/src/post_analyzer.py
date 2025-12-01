"""
Post Analyzer Module

Analyzes individual Instagram posts:
- Extracts and classifies comments
- Calculates engagement metrics
- Computes Engagement Quality Score (EQS)
"""

import logging
from typing import Dict, List, Tuple
from comment_classifier import classify_comment

logger = logging.getLogger(__name__)


def analyze_post_comments(comments: List[str]) -> Dict[str, float]:
    """
    Analyze comments and calculate classification percentages.
    
    Args:
        comments (List[str]): List of comment text strings
        
    Returns:
        Dict[str, float]: Dictionary with text_percentage, emoji_percentage, mixed_percentage
    """
    if not comments:
        return {
            'text_percentage': 0.0,
            'emoji_percentage': 0.0,
            'mixed_percentage': 0.0
        }
    
    text_count = 0
    emoji_count = 0
    mixed_count = 0
    
    for comment in comments:
        classification = classify_comment(comment)
        if classification == "text":
            text_count += 1
        elif classification == "emoji":
            emoji_count += 1
        elif classification == "mixed":
            mixed_count += 1
    
    total = len(comments)
    
    return {
        'text_percentage': round((text_count / total) * 100, 2),
        'emoji_percentage': round((emoji_count / total) * 100, 2),
        'mixed_percentage': round((mixed_count / total) * 100, 2)
    }


def calculate_unique_commenters_ratio(comments: List[str]) -> float:
    """
    Calculate the ratio of unique commenters.
    For now, we approximate this by counting unique comments.
    In a full implementation, you'd extract usernames from comments.
    
    Args:
        comments (List[str]): List of comment text strings
        
    Returns:
        float: Unique commenters ratio (unique_comments / total_comments)
    """
    if not comments:
        return 0.0
    
    # Normalize comments for comparison (lowercase, strip whitespace)
    unique_comments = set()
    for comment in comments:
        normalized = ' '.join(comment.lower().strip().split())
        if normalized:
            unique_comments.add(normalized)
    
    total = len(comments)
    unique_count = len(unique_comments)
    
    ratio = unique_count / total if total > 0 else 0.0
    return round(ratio, 4)


def calculate_eqs(
    text_percentage: float,
    mixed_percentage: float,
    emoji_percentage: float,
    unique_commenters_ratio: float
) -> float:
    """
    Calculate Engagement Quality Score (EQS).
    
    Formula:
    EQS = (Text% * 0.6) + (Mixed% * 0.3) - (Emoji% * 0.1) + (Unique commenters ratio * 0.2)
    
    Args:
        text_percentage (float): Percentage of text-only comments
        mixed_percentage (float): Percentage of mixed comments
        emoji_percentage (float): Percentage of emoji-only comments
        unique_commenters_ratio (float): Ratio of unique commenters
        
    Returns:
        float: Engagement Quality Score
    """
    # Normalize percentages to 0-1 scale for calculation
    text_score = (text_percentage / 100.0) * 0.6
    mixed_score = (mixed_percentage / 100.0) * 0.3
    emoji_penalty = (emoji_percentage / 100.0) * 0.1
    uniqueness_score = unique_commenters_ratio * 0.2
    
    eqs = text_score + mixed_score - emoji_penalty + uniqueness_score
    
    # Scale back to 0-100 range for readability
    eqs_scaled = eqs * 100
    
    return round(eqs_scaled, 2)


def check_pass_criteria(
    total_comments: int,
    text_percentage: float,
    mixed_percentage: float,
    minimum_comments_required: int,
    minimum_text_percentage_required: float
) -> bool:
    """
    Check if a post passes the Phase-1 criteria.
    
    Args:
        total_comments (int): Total number of comments
        text_percentage (float): Percentage of text-only comments
        mixed_percentage (float): Percentage of mixed comments
        minimum_comments_required (int): Minimum comments required
        minimum_text_percentage_required (float): Minimum text-based percentage required
        
    Returns:
        bool: True if post passes criteria, False otherwise
    """
    if total_comments < minimum_comments_required:
        return False
    
    # Text-based includes both text-only and mixed comments
    text_based_percentage = text_percentage + mixed_percentage
    
    return text_based_percentage >= minimum_text_percentage_required


def analyze_post(
    comments: List[str],
    minimum_comments_required: int,
    minimum_text_percentage_required: float
) -> Dict:
    """
    Complete analysis of a single post.
    
    Args:
        comments (List[str]): List of comment text strings
        minimum_comments_required (int): Minimum comments required
        minimum_text_percentage_required (float): Minimum text-based percentage required
        
    Returns:
        Dict: Complete post analysis results
    """
    total_comments = len(comments)
    
    # Calculate classification percentages
    percentages = analyze_post_comments(comments)
    
    # Calculate unique commenters ratio
    unique_ratio = calculate_unique_commenters_ratio(comments)
    
    # Calculate EQS
    eqs = calculate_eqs(
        percentages['text_percentage'],
        percentages['mixed_percentage'],
        percentages['emoji_percentage'],
        unique_ratio
    )
    
    # Check pass/fail
    passes = check_pass_criteria(
        total_comments,
        percentages['text_percentage'],
        percentages['mixed_percentage'],
        minimum_comments_required,
        minimum_text_percentage_required
    )
    
    return {
        'total_comments': total_comments,
        'text_percentage': percentages['text_percentage'],
        'emoji_percentage': percentages['emoji_percentage'],
        'mixed_percentage': percentages['mixed_percentage'],
        'unique_commenters_ratio': unique_ratio,
        'EQS': eqs,
        'pass': 'Pass' if passes else 'Fail'
    }

