#!/usr/bin/env python3
"""Which languages the site actually offers — read from the generator.

There is exactly one place that decides this, `UNLISTED_LANGS` in
`build_i18n.py`, and every gate stage has to agree with it. They did not:
`i18n_qa.py` kept its own copy of the list and `switcher.py` and
`page_shell.py` hardcoded de/en/fr outright, so switching localisation off
made three stages fail on a build that was correct.

Copying the list into each stage is what caused that, so this reads the
generator rather than restating it. Turning localisation back on stays a
one-line edit in `build_i18n.py`, and the gate follows on its own.

Parsed rather than imported, because importing `build_i18n` would pull in
beautifulsoup4 and the gate must run without it.
"""
import io
import os


def offered(root):
    """['en'] plus every language build_i18n.py still offers to visitors."""
    src = io.open(os.path.join(root, "build_i18n.py"), encoding="utf-8").read()

    def declared(marker, close):
        # anchored on the line start, so LISTED_LANGS and UNLISTED_LANGS are
        # never mistaken for the LANGS declaration
        at = src.index("\n" + marker) + len(marker) + 1
        raw = src[at:src.index(close, at)]
        return [w.strip().strip('"').strip("'") for w in raw.split(",") if w.strip()]

    langs = declared("LANGS = [", "]")
    unlisted = declared("UNLISTED_LANGS = {", "}")
    return ["en"] + [l for l in langs if l not in unlisted]


def localisation_is_off(root):
    """True when English is the only language a visitor is offered."""
    return offered(root) == ["en"]
