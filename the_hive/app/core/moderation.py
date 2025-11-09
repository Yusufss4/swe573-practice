"""
Content moderation utilities for comments.

SRS Requirements:
- FR-10.2: Basic automated text moderation
- FR-10.3: Profanity and inappropriate content filtering
"""
import re
from typing import Tuple


# Basic profanity word list (placeholder - in production use a proper library)
PROFANITY_LIST = {
    "spam", "scam", "fraud", "fake", "stupid", "idiot", "hate",
    "terrible", "awful", "worst", "horrible", "disgusting",
    # Add more words as needed
}

# Patterns that might indicate spam or inappropriate content
SPAM_PATTERNS = [
    r'(?i)(click here|buy now|limited offer|act now)',
    r'(?i)(http://|https://|www\.)',  # URLs
    r'(?i)(call|text|whatsapp)\s*\d{3}',  # Phone numbers
    r'(?i)(\$\d+|\d+\s*dollars?)',  # Money references
]


def check_profanity(text: str) -> Tuple[bool, list[str]]:
    """
    Check text for profanity and inappropriate content.
    
    Args:
        text: The text to check
        
    Returns:
        Tuple of (has_profanity: bool, found_words: list[str])
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    found_profanity = []
    for word in words:
        if word in PROFANITY_LIST:
            found_profanity.append(word)
    
    return len(found_profanity) > 0, found_profanity


def check_spam_patterns(text: str) -> Tuple[bool, list[str]]:
    """
    Check text for spam patterns.
    
    Args:
        text: The text to check
        
    Returns:
        Tuple of (has_spam: bool, matched_patterns: list[str])
    """
    matched = []
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text):
            matched.append(pattern)
    
    return len(matched) > 0, matched


def moderate_content(text: str) -> Tuple[bool, str]:
    """
    Moderate comment content for profanity and spam.
    
    SRS Requirement FR-10.2: Automated text moderation
    
    Args:
        text: The comment text to moderate
        
    Returns:
        Tuple of (is_approved: bool, reason: str)
        - is_approved: True if content passes moderation
        - reason: Explanation if content is flagged
    """
    # Check length
    if len(text.strip()) < 10:
        return False, "Comment too short (minimum 10 characters)"
    
    if len(text) > 1000:
        return False, "Comment too long (maximum 1000 characters)"
    
    # Check for profanity
    has_profanity, profane_words = check_profanity(text)
    if has_profanity:
        return False, f"Contains inappropriate language: {', '.join(profane_words)}"
    
    # Check for spam patterns
    has_spam, spam_patterns = check_spam_patterns(text)
    if has_spam:
        return False, "Contains spam or promotional content"
    
    # Check for excessive capitalization (more than 50% caps)
    alpha_chars = [c for c in text if c.isalpha()]
    if alpha_chars:
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if caps_ratio > 0.5:
            return False, "Excessive use of capital letters"
    
    # Check for excessive repetition
    if re.search(r'(.)\1{4,}', text):  # Same character repeated 5+ times
        return False, "Excessive character repetition"
    
    # All checks passed
    return True, ""


def sanitize_content(text: str) -> str:
    """
    Sanitize comment content by removing extra whitespace.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove multiple newlines first (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces (but not newlines) with single space
    text = re.sub(r' +', ' ', text)
    
    return text
