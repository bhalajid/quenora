#!/usr/bin/env python3
"""
build_form.py — what the enquiry form accepts, and what it shows you.

THE COUNTRY CODE

Asked for directly, and I had argued against it. The argument was that a
dropdown is a control to operate before you have written anything, and that a
list of two hundred countries needs localising into three languages for a
field that is optional. Both are still true of a two-hundred-row list.

They stop being true of a short one. This firm works from Heilbronn into
Europe, in German, French and English — so the list is the places it actually
works, longest-serving first, with a free-text option for everywhere else. It
is nine rows, the codes are the same characters in every language, and the
number field beside it keeps taking a national number for anyone who ignores
the whole thing.

The select writes into the phone field rather than submitting separately, so
the endpoint keeps receiving one string and nothing downstream changes.

THE REST

Name and phone rules came from a QA report: a name cannot be a number and a
phone cannot be words. The placeholder shows the format the firm's own numbers
use, so the field says what it wants before anyone types.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = '152 3392 7436'

# Where the firm actually works, plus a way out. Codes read the same in every
# language, so this needs no translation beyond the last row.
CODES = [('+49', 'Germany'), ('+43', 'Austria'), ('+41', 'Switzerland'),
         ('+33', 'France'), ('+31', 'Netherlands'), ('+32', 'Belgium'),
         ('+44', 'United Kingdom'), ('+1', 'United States / Canada'),
         ('', 'Other')]

SELECT_CSS = """/*FORM:CSS*/
.phonerow{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px}
.phonerow select{font-family:'JetBrains Mono',ui-monospace,monospace;
  font-size:16px;color:var(--t1);background:rgba(20,22,30,.6);
  border:1px solid var(--line2);border-radius:2px;padding:0 10px;height:100%;
  min-height:46px;cursor:pointer}
.phonerow select:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
/*/FORM:CSS*/"""


def main():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<input[^>]*id="cfPhone"[^>]*?>', s)
    if not m:
        print('  form: no phone field'); return 0
    tag = m.group(0)
    # Do not return early on the placeholder. It was added in an earlier build,
    # so that guard also skipped the country select that comes after it — the
    # select sat in this file for a build and never reached a page.
    if 'placeholder=' in tag:
        new = tag
    else:
        new = tag.replace('type="tel"', 'type="tel" placeholder="%s"' % PLACEHOLDER)
    s = s.replace(tag, new, 1)

    # wrap the field with a code select, and keep one value on the wire
    if 'id="cfCode"' not in s:
        opts = ''.join(
            '<option value="%s"%s>%s%s</option>' % (
                c, ' selected' if c == '+49' else '',
                c + '  ' if c else '', name)
            for c, name in CODES)
        row = ('<div class="phonerow">'
               '<label class="vh" for="cfCode">Country code</label>'
               '<select id="cfCode">' + opts + '</select>'
               + new + '</div>')
        s = s.replace(new, row, 1)
        js = """<script>
/* The select writes into the phone field rather than submitting on its own,
   so the endpoint still receives one string and nothing downstream changes. */
(function(){
  if (typeof document === 'undefined' ||
      typeof document.addEventListener !== 'function') return;
  var sel = document.getElementById('cfCode');
  var tel = document.getElementById('cfPhone');
  if (!sel || !tel) return;
  function apply(){
    var code = sel.value;
    var rest = tel.value.replace(/^\s*\+\d{1,3}\s*/, '').trim();
    tel.value = code ? (code + ' ' + rest).trim() : rest;
  }
  sel.addEventListener('change', apply);
  tel.addEventListener('blur', function(){
    if (sel.value && tel.value && tel.value.charAt(0) !== '+') apply();
  });
})();
</script>"""
        s = s.replace('</body>', js + '\n</body>', 1)
        if '/*FORM:CSS*/' not in s:
            i = s.rindex('</style>')
            s = s[:i] + SELECT_CSS + '\n' + s[i:]
        print('  form: a country code select, %d entries' % len(CODES))

    open(p, 'w', encoding='utf-8').write(s)
    print('  form: the phone field shows the format it wants')
    return 0


if __name__ == '__main__':
    sys.exit(main())
