from app.services.pii_service import redact_pii

def test_redact_email():
    text = "My email is support@majiguard.com"
    redacted = redact_pii(text)
    assert "[EMAIL REDACTED]" in redacted
    assert "support@majiguard.com" not in redacted

def test_redact_phone():
    text = "Reach out to me at +254 712 345678 or 0722123456"
    redacted = redact_pii(text)
    assert "[PHONE REDACTED]" in redacted
    assert "+254 712 345678" not in redacted
    assert "0722123456" not in redacted

def test_redact_names():
    text = "Hello, my name is John Doe. I am reporting from the school."
    redacted = redact_pii(text)
    assert "[NAME REDACTED]" in redacted
    assert "John Doe" not in redacted

def test_redact_multiple():
    text = "Reported by Sarah Smith (email: sarah@gmail.com, phone: 0712345678)"
    redacted = redact_pii(text)
    assert "[NAME REDACTED]" in redacted
    assert "[EMAIL REDACTED]" in redacted
    assert "[PHONE REDACTED]" in redacted
