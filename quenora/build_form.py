#!/usr/bin/env python3
"""
build_form.py — what the enquiry form accepts, and what it shows you.

The name and phone rules were added after a QA report and they work: a name
cannot be a number and a phone cannot be words. What was missing is the part a
visitor actually sees before they type — nothing on screen said the phone
wanted a country code, so a German visitor writes 0152 and an international
one guesses.

A country dropdown is the usual answer and the wrong one here. It is a control
to operate before you have written anything, it needs a flag set or a list of
two hundred names to localise, and the field is optional. A placeholder in the
format the firm's own numbers use costs nothing, works in every language, and
tells the visitor the same thing: lead with the code.

The pattern still accepts 0152/3392736 without one, because rejecting a
national number on an optional field would be pedantry.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = '+49 152 3392 7436'


def main():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<input[^>]*id="cfPhone"[^>]*?>', s)
    if not m:
        print('  form: no phone field'); return 0
    tag = m.group(0)
    if 'placeholder=' in tag:
        print('  form: the phone field already shows its format'); return 0
    new = tag.replace('type="tel"', 'type="tel" placeholder="%s"' % PLACEHOLDER)
    open(p, 'w', encoding='utf-8').write(s.replace(tag, new, 1))
    print('  form: the phone field shows the country-code format')
    return 0


if __name__ == '__main__':
    sys.exit(main())
