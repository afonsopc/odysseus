"""needs_auto_name must not flag a user's multi-word title as a placeholder.

The frontend default name is "<modelid> HH:MM:SS AM/PM" where <modelid> is a
single no-space token. needs_auto_name matched it with `^.+ \\d...`, whose
`.+` also matched a deliberately chosen multi-word title ending in a clock
time (e.g. "Call with Bob 3:45:00 PM"), so the background auto-namer silently
overwrote the user's title. The prefix must be a single token.
"""
from routes.chat_helpers import needs_auto_name


def test_real_default_names_are_flagged():
    assert needs_auto_name("gpt-4o 10:23:45 PM") is True
    assert needs_auto_name("claude-3-opus 9:30:00 AM") is True


def test_multiword_user_title_is_kept():
    assert needs_auto_name("Call with Bob 3:45:00 PM") is False
    assert needs_auto_name("Sprint planning 9:00:00 AM") is False
    assert needs_auto_name("Notes re budget 12:00:00 PM") is False


def test_other_placeholders_still_flagged():
    assert needs_auto_name("") is True
    assert needs_auto_name("Chat") is True
    assert needs_auto_name("Chat: hello") is True


def test_normal_title_kept():
    assert needs_auto_name("Trip itinerary") is False
