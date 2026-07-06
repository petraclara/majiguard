import re

def redact_pii(text: str) -> str:
    """Redacts PII such as email addresses, phone numbers, and name introductions."""
    if not text:
        return ""
    
    # 1. Redact email addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    redacted = re.sub(email_pattern, "[EMAIL REDACTED]", text)
    
    # 2. Redact phone numbers
    # Matches international format like +123-456-7890, +254 712 345678, or simple digits of length 7-15
    phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{0,4}|\b\d{9,12}\b'
    # We want to be careful not to redact simple duration indicators like "3 days" or times like "4 AM"
    # So we only redact phone-like structures.
    redacted = re.sub(phone_pattern, "[PHONE REDACTED]", redacted)
    
    # 3. Redact common name introductions (e.g. "I am John Doe", "My name is Sarah")
    name_intro_patterns = [
        (r'(?i)\bmy name is\s+([a-z]+(?:\s+[a-z]+){0,2})', "my name is [NAME REDACTED]"),
        (r'(?i)\bi am\s+([a-z]+(?:\s+[a-z]+){0,2})\b', "i am [NAME REDACTED]"),
        (r'(?i)\breported by\s+([a-z]+(?:\s+[a-z]+){0,2})', "reported by [NAME REDACTED]"),
        (r'(?i)\bcontact\s+([a-z]+(?:\s+[a-z]+){0,2})', "contact [NAME REDACTED]"),
    ]
    for pattern, repl in name_intro_patterns:
        redacted = re.sub(pattern, repl, redacted)
        
    return redacted
