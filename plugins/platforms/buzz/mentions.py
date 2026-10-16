"""Text addressing for Buzz: references inside data are not mentions."""

import re


# Deliberately local, not a Markdown renderer: mask URLs, code and explicitly
# delimited quotations without changing the message delivered to the gateway.
_REFERENCE_RE = re.compile(
    r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})[^\n]*\n.*?"
    r"(?:^[ \t]{0,3}(?P=fence)[`~]*[ \t]*(?=\n|$)|\Z)"
    r"|^[ \t]*>[^\n]*"
    r"|(?P<ticks>`+)(?!`).*?(?<!`)(?P=ticks)(?!`)"
    r"|\b[a-z][a-z0-9+.-]*://[^\s<>`\"'‘’“”]+"
    r'|"[^"\n]*"|“[^”\n]*”|‘[^’\n]*’'
    r"|(?<!\w)'[^'\n]*'(?!\w)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def addressing_text(content: str) -> str:
    """Keep prose for inbound gating and outbound p-tag resolution only."""
    return _REFERENCE_RE.sub(" ", content)


def is_mentioned(content: str, pubkey: str, npub: str, display_name: str) -> bool:
    """Match the supported bare hex/npub and @name addresses outside data."""
    lowered = addressing_text(content).lower()
    patterns = []
    if pubkey and re.fullmatch(r"[0-9a-f]{64}", pubkey):
        patterns.append(rf"(?<![0-9a-f]){re.escape(pubkey)}(?![0-9a-f])")
    if npub:
        patterns.append(rf"(?<![a-z0-9]){re.escape(npub.lower())}(?![a-z0-9])")
    if display_name:
        patterns.append(rf"(?<![\w@])@{re.escape(display_name.lower())}" + r"(?=$|[\s,;.!?:)\]}])")
    return any(re.search(p, lowered) for p in patterns)
