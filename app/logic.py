import re
from typing import Optional, Tuple, List

PING_TXT = "ping"

# الگوی سناریوی صفر
RE_BASE = re.compile(r"^return\s+base\s+random\s+key:\s*(.+)$", re.IGNORECASE)
RE_MEMBER = re.compile(r"^return\s+member\s+random\s+key:\s*(.+)$", re.IGNORECASE)

def handle_sanity(text: str) -> Tuple[Optional[str], Optional[List[str]], Optional[List[str]]]:
    t = text.strip()
    if t.lower() == PING_TXT:
        return "pong", None, None

    m = RE_BASE.match(t)
    if m:
        key = m.group(1).strip()
        return None, [key], None

    m = RE_MEMBER.match(t)
    if m:
        key = m.group(1).strip()
        return None, None, [key]

    return None, None, None
