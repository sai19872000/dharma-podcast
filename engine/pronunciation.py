"""
pronunciation.py — Sanskrit/Pāli/Indian-name IPA pronunciation table.

Used by tts.py to wrap known terms in ElevenLabs phoneme tags before TTS.

Substitution is order-sensitive: longer/compound terms are applied FIRST
to prevent partial-match overlap (e.g. "Bhagavad Gītā" before "Gītā").

Public API:
    apply_phoneme_substitution(text: str) -> str
        Wraps known terms in <phoneme alphabet="ipa" ph="...">term</phoneme>.
        Falls back to spelling hints if ElevenLabs model doesn't support phoneme tags.
    PRONUNCIATION_TABLE: dict[str, str]
        Maps term (as it appears in script text) → IPA string.

IPA renderings use Indian-English/Sanskrit-friendly phonology:
    - ʋ  for v (bilabial approximant, common in Hindi/Sanskrit)
    - ɾ  for intervocalic r (tap, not American rhotic)
    - ʂ  for retroflex sh (ṣ)
    - ɳ  for retroflex n (ṇ)
    - ɲ  for palatal n (ñ)
    - d͡ʒ for the affricate j in Sanskrit/Indian borrowings
    - ː  for long vowels
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# PRONUNCIATION_TABLE
# Key: the term exactly as it appears in the script (with diacritics or not).
# Value: IPA pronunciation string.
#
# Order in this dict does NOT matter — apply_phoneme_substitution sorts by
# term length (descending) to prevent partial-match overlap.
# ---------------------------------------------------------------------------

PRONUNCIATION_TABLE: dict[str, str] = {
    # Compound terms / multi-word phrases — must be matched before single words
    "Bhagavad Gītā":        "/bʱəɡəʋəd ɡiːtaː/",
    "Yoga Sūtra":           "/joːɡə suːtɾə/",
    "Yoga Sūtras":          "/joːɡə suːtɾəz/",
    "Saṃyutta Nikāya":      "/səmjʊtːə nɪkaːjə/",
    "Aṅguttara Nikāya":     "/əŋɡʊtːəɾə nɪkaːjə/",
    "niṣkāma karma":        "/nɪʂkaːmə kəɾmə/",
    "Upaniṣad":             "/ʊpənɪʂəd/",
    "Upaniṣads":            "/ʊpənɪʂədz/",

    # Single-word Sanskrit/Pāli concept terms
    "vairāgya":             "/ʋəɪˈɾaːɡjə/",
    "abhyāsa":              "/əˈbʱjaːsə/",
    "sthitaprajña":         "/stʱɪtəˈpɾəd͡ʒɲə/",
    "ātman":                "/ˈaːtmən/",
    "anattā":               "/əˈnətːaː/",
    "sākṣī":                "/ˈsaːkʂiː/",
    "dhyāna":               "/ˈdʱjaːnə/",
    "nibbidā":              "/nɪˈbɪdaː/",
    "samādhi":              "/səˈmaːdʱɪ/",
    "mokṣa":                "/ˈmoːkʂə/",
    "samvāda":              "/ˈsəmʋaːdə/",
    "ṛṣi":                  "/ˈɾɪʂɪ/",

    # Proper names — figures
    "Patañjali":            "/pəˈtəɲd͡ʒəli/",
    "Kṛṣṇa":               "/ˈkɾɪʂɳə/",
    "Arjuna":               "/ˈəɾd͡ʒʊnə/",
    "Vyāsa":                "/ˈʋjaːsə/",
    "Śaṅkara":              "/ˈʃəŋkəɾə/",
    "Nāgārjuna":            "/naːˈɡaːɾd͡ʒʊnə/",

    # Alternate spellings / common romanizations without diacritics
    "Krishna":              "/ˈkɾɪʂɳə/",
    "Arjun":                "/ˈəɾd͡ʒʊn/",
    "Shankara":             "/ˈʃəŋkəɾə/",
    "Nagarjuna":            "/naːˈɡaːɾd͡ʒʊnə/",
}

# ---------------------------------------------------------------------------
# Sort keys by length descending — longer terms matched first to avoid
# "Gītā" matching inside "Bhagavad Gītā" before the compound is handled.
# ---------------------------------------------------------------------------
_SORTED_TERMS: list[tuple[str, str]] = sorted(
    PRONUNCIATION_TABLE.items(), key=lambda kv: len(kv[0]), reverse=True
)


def apply_phoneme_substitution(text: str) -> str:
    """
    Wrap each occurrence of a known Sanskrit/Pāli/Indian term in an
    ElevenLabs-compatible phoneme tag:

        <phoneme alphabet="ipa" ph="...">term</phoneme>

    Terms are processed longest-first to avoid partial-match overlap
    (e.g. compound "Bhagavad Gītā" is replaced before shorter components).

    Already-tagged spans are preserved: the text is split into tagged
    and untagged segments; substitution only runs on untagged segments.
    """
    for term, ipa in _SORTED_TERMS:
        replacement = f'<phoneme alphabet="ipa" ph="{ipa}">{term}</phoneme>'
        text = _sub_outside_tags(text, term, replacement)
    return text


def _sub_outside_tags(text: str, term: str, replacement: str) -> str:
    """
    Replace `term` with `replacement` only in text segments that are NOT
    already inside a <phoneme ...>...</phoneme> tag.

    Strategy: split on existing phoneme tags, apply substitution only to
    the plain-text segments, then reassemble.
    """
    # Split text into alternating [plain, tagged, plain, tagged, …] segments.
    # Regex: match an existing <phoneme ...>...</phoneme> block.
    tag_pattern = re.compile(
        r'<phoneme\s[^>]*>.*?</phoneme>', re.DOTALL
    )
    parts: list[str] = []
    last_end = 0
    for m in tag_pattern.finditer(text):
        plain = text[last_end:m.start()]
        parts.append(plain.replace(term, replacement))  # substitute in plain segment
        parts.append(m.group())                         # preserve tagged segment as-is
        last_end = m.end()
    # Tail segment after the last tag
    parts.append(text[last_end:].replace(term, replacement))
    return "".join(parts)
