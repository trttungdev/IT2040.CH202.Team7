"""
PI detectors: the paper's proposal (R&R) and the prior framework it improves
on (WIMBD), side by side in one file for easy reuse/comparison.

R&R -- "Personal Information Parroting in Language Models" (Subramani,
Ghate, Diab), Section 2 / Appendix A. Regexes transcribed close to verbatim
from Appendix A.1-A.3; rules follow the same appendix's prose exactly
(context trigger words, alphanumeric density check, NANP validation,
placeholder denylist).

WIMBD -- Elazar et al. 2023, "What's In My Big Data?", reconstructed from
the paper's description of it (no source available): only 3 detector types
(email, IPv4, phone-no-country-code), no IPv6, no +1-country-code phone,
and none of R&R's post-processing rules.
"""

import re
from dataclasses import dataclass


@dataclass
class Detection:
    pi_type: str
    span: str
    start: int
    end: int


# =============================================================================
# R&R (the paper's proposal)
# =============================================================================

# A.1 Email addresses (case-insensitive; local-part allows a dotted-atom form
# or a quoted-string form, domain allows a dotted-label form or a
# domain-literal form, e.g. [192.168.1.1] or a general-address-literal).
RR_EMAIL_RE = re.compile(
    r"(?:[a-z0-9]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]"
    r"|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")"
    r"@"
    r"(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    r"|\[(?:(?:2(?:5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])\.){3}"
    r"(?:2(?:5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])"
    r"|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]"
    r"|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+\])",
    re.IGNORECASE,
)

# A.2 IPv4
RR_IPV4_RE = re.compile(
    r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
)

# A.2 IPv6 (full form incl. link-local %zone and embedded-IPv4 tail forms)
RR_IPV6_RE = re.compile(
    r"(?:^|(?<=\s))"
    r"(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,7}:"
    r"|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}"
    r"|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})"
    r"|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)"
    r"|fe80:(?:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,})"
    r"|::(?:ffff(?::0{1,4}){0,1}:){0,1}"
    r"(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    r"|(?:[0-9a-fA-F]{1,4}:){1,4}"
    r"(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    r")(?=\s|$)"
)

# A.3 US/Canada 10-digit phone number, no country code.
RR_PHONE_RE = re.compile(r"\s+\(?(\d{3})\)?[-. ]*(\d{3})[-. ]?(\d{4})(?!\d)")

# A.3 US/Canada phone number with a leading +1 / 1 country code.
RR_PHONE_PLUS1_RE = re.compile(r"\s+(?:\+1|1)[-. ]*\(?(\d{3})\)?[-. ]*(\d{3})[-. ]?(\d{4})(?!\d)")

# A.2/A.3: words in the 20-char micro-context that indicate an ID/serial/
# grant number rather than real PI.
RR_CONTEXT_TRIGGER_WORDS = [
    "isbn", "doi", "#", "grant", "award", "nsf", "patent", "usf", "edition",
    "congress", "appeal", "claim", "exhibit", "serial", "pin", "receipt",
    "case", "tracking", "ticket", "route", " wo ", "volume",
]

# A.3: placeholder numbers explicitly excluded.
RR_PLACEHOLDER_NUMBERS = {
    "1234567890", "2345678910", "2147483647", "73737373", "3141592653",
}

# A.3: NANP area-code / central-office-code validation. Both the area code
# and central office code must not start with 0 or 1.
RR_VALID_NANP_CODE_RE = re.compile(r"^[2-9]\d{2}$")


def _rr_context_has_trigger_word(text: str, start: int, window: int = 20) -> bool:
    ctx = text[max(0, start - window):start].lower()
    return any(w in ctx for w in RR_CONTEXT_TRIGGER_WORDS)


def _rr_prefix_alnum_density_ok(text: str, start: int, window: int = 50, min_ratio: float = 0.10) -> bool:
    ctx = text[max(0, start - window):start]
    if not ctx:
        return False
    alnum = sum(c.isalnum() for c in ctx)
    return (alnum / len(ctx)) >= min_ratio


def _rr_validate_nanp(area: str, office: str) -> bool:
    return bool(RR_VALID_NANP_CODE_RE.match(area) and RR_VALID_NANP_CODE_RE.match(office))


def rr_detect_emails(text: str) -> list[Detection]:
    """A.1: regex match, then split on '@', reject empty/leading-or-trailing-
    dot domains, and require a '.' in the domain."""
    out = []
    for m in RR_EMAIL_RE.finditer(text):
        span = m.group(0)
        if "@" not in span:
            continue
        user, _, domain = span.partition("@")
        if not user or not domain:
            continue
        if domain.startswith(".") or domain.endswith("."):
            continue
        if "." not in domain:
            continue
        out.append(Detection("email", span, m.start(), m.end()))
    return out


def rr_detect_ips(text: str) -> list[Detection]:
    """A.2: regex match, then trigger-word + alphanumeric-density rules."""
    out = []
    for pattern, pi_type in ((RR_IPV4_RE, "ip_v4"), (RR_IPV6_RE, "ip_v6")):
        for m in pattern.finditer(text):
            start = m.start()
            if _rr_context_has_trigger_word(text, start):
                continue
            if not _rr_prefix_alnum_density_ok(text, start):
                continue
            out.append(Detection(pi_type, m.group(0), start, m.end()))
    return out


def rr_detect_phones(text: str) -> list[Detection]:
    """A.3: regex match (both variants), then trigger-word, alphanumeric-
    density, placeholder-denylist, and NANP validation rules. The +1
    variant is checked first and takes priority over the bare 10-digit
    variant on overlapping spans."""
    out = []
    seen_spans: list[tuple[int, int]] = []

    for m in RR_PHONE_PLUS1_RE.finditer(text):
        area, office, rest = m.groups()
        start = m.start()
        if (area + office + rest) in RR_PLACEHOLDER_NUMBERS:
            continue
        if _rr_context_has_trigger_word(text, start):
            continue
        if not _rr_prefix_alnum_density_ok(text, start):
            continue
        if not _rr_validate_nanp(area, office):
            continue
        out.append(Detection("phone_plus1", m.group(0).strip(), start, m.end()))
        seen_spans.append((m.start(), m.end()))

    for m in RR_PHONE_RE.finditer(text):
        start, end = m.start(), m.end()
        if any(not (end <= s or start >= e) for s, e in seen_spans):
            continue  # already captured by the +1 variant
        area, office, rest = m.groups()
        if (area + office + rest) in RR_PLACEHOLDER_NUMBERS:
            continue
        if _rr_context_has_trigger_word(text, start):
            continue
        if not _rr_prefix_alnum_density_ok(text, start):
            continue
        if not _rr_validate_nanp(area, office):
            continue
        out.append(Detection("phone", m.group(0).strip(), start, end))

    return out


def rr_detect_all(text: str) -> list[Detection]:
    return rr_detect_emails(text) + rr_detect_ips(text) + rr_detect_phones(text)


# =============================================================================
# WIMBD (the prior framework R&R improves on)
# =============================================================================

# Plain, permissive email regex -- no quoted-string local part, no
# domain-literal support, no post-hoc "@"/domain sanity checks.
WIMBD_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Same base IPv4 pattern as R&R -- the paper doesn't claim R&R changed IPv4
# detection, only that it added IPv6 on top.
WIMBD_IPV4_RE = re.compile(
    r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
)

# US 10-digit phone number, no country-code variant, no NANP validation,
# no trigger-word/alphanumeric-density filtering applied downstream.
WIMBD_PHONE_RE = re.compile(r"\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}")


def wimbd_detect_emails(text: str) -> list[Detection]:
    return [Detection("email", m.group(0), m.start(), m.end()) for m in WIMBD_EMAIL_RE.finditer(text)]


def wimbd_detect_ips(text: str) -> list[Detection]:
    return [Detection("ip_v4", m.group(0), m.start(), m.end()) for m in WIMBD_IPV4_RE.finditer(text)]


def wimbd_detect_phones(text: str) -> list[Detection]:
    return [Detection("phone", m.group(0), m.start(), m.end()) for m in WIMBD_PHONE_RE.finditer(text)]


def wimbd_detect_all(text: str) -> list[Detection]:
    return wimbd_detect_emails(text) + wimbd_detect_ips(text) + wimbd_detect_phones(text)
