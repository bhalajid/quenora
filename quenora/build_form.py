#!/usr/bin/env python3
"""
build_form.py — what the enquiry form accepts, and what it shows you.

THE COUNTRY CODE

Asked for directly, and I had argued against it. The argument was that a
dropdown is a control to operate before you have written anything, and that a
list of two hundred countries needs localising into three languages for a
field that is optional. Both are still true of a two-hundred-row list.

They stop being true of a short one. This firm works from Bad Friedrichshall into
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
/* the box that replaces the select when the country is not one of the eight.
   Same metrics, so the row does not jump when it swaps. */
.phonerow .codebox{font-family:'JetBrains Mono',ui-monospace,monospace;
  font-size:16px;color:var(--t1);background:rgba(20,22,30,.6);
  border:1px solid var(--line2);border-radius:2px;padding:0 10px;height:100%;
  min-height:46px;width:7ch}
.phonerow .codebox:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
/*/FORM:CSS*/"""


JS = """<script>/*FORM:JS*/
/* The select writes into the phone field rather than submitting on its own,
   so the endpoint still receives one string and nothing downstream changes. */
(function(){
  if (typeof document === 'undefined' ||
      typeof document.addEventListener !== 'function') return;
  var sel = document.getElementById('cfCode');
  var tel = document.getElementById('cfPhone');
  if (!sel || !tel) return;

  /* "Other" used to mean no code at all, which left a visitor outside the
     eight listed countries with nowhere to put theirs. Choosing it swaps the
     select for a small box that starts at + and takes digits only. Emptying
     the box, or pressing Escape, brings the list back — otherwise the choice
     is one-way and the reader is stranded in a field they opened by
     accident. */
  var other = document.createElement('input');
  other.type = 'tel';
  other.id = 'cfCodeOther';
  other.className = 'codebox';
  other.setAttribute('inputmode', 'numeric');
  other.setAttribute('aria-label', 'Country code');
  other.setAttribute('maxlength', '5');
  other.placeholder = '+';
  other.hidden = true;
  sel.parentNode.insertBefore(other, sel.nextSibling);

  function usingOther(){ return !other.hidden; }
  function code(){ return usingOther() ? other.value.trim() : sel.value; }

  function apply(){
    var c = code();
    var rest = tel.value.replace(/^\s*\+\d{1,3}\s*/, '').trim();
    tel.value = (c && c !== '+') ? (c + ' ' + rest).trim() : rest;
  }

  function showList(){
    other.hidden = true; sel.hidden = false;
    sel.value = '+49'; apply();
  }

  sel.addEventListener('change', function(){
    if (sel.value === '') {          /* Other */
      sel.hidden = true; other.hidden = false;
      other.value = '+';
      other.focus();
      var n = other.value.length;
      try { other.setSelectionRange(n, n); } catch (e) {}
    } else {
      apply();
    }
  });

  /* digits only, and always exactly one leading + */
  other.addEventListener('input', function(){
    var digits = other.value.replace(/[^0-9]/g, '').slice(0, 4);
    other.value = '+' + digits;
    apply();
  });
  other.addEventListener('keydown', function(e){
    if (e.key === 'Escape') { showList(); sel.focus(); }
  });
  other.addEventListener('blur', function(){
    if (other.value === '' || other.value === '+') showList();
  });

  tel.addEventListener('blur', function(){
    var c = code();
    if (c && c !== '+' && tel.value && tel.value.charAt(0) !== '+') apply();
  });
})();
/*/FORM:JS*/</script>"""


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
        # Normalise rather than leave alone. The field sits behind a country
        # select that already shows +49, so a placeholder carrying the code as
        # well told the reader to type it twice.
        new = re.sub(r'placeholder="[^"]*"', 'placeholder="%s"' % PLACEHOLDER, tag)
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

        print('  form: a country code select, %d entries' % len(CODES))

    # Apply the script and the stylesheet on EVERY run, not only on the run
    # that first inserted the select. Guarding both behind "does the select
    # exist yet" meant an already-built page kept whatever script it was given
    # the first time, so any change here never reached a built page — the same
    # trap as the placeholder above. Delimited and idempotent now, the way the
    # widget and the preview stylesheet already are.
    if '/*FORM:JS*/' in s:
        s = re.sub(r'<script>/\*FORM:JS\*/.*?/\*/FORM:JS\*/</script>',
                   lambda _m: JS, s, flags=re.S)
    else:
        s = s.replace('</body>', JS + '\n</body>', 1)
    if '/*FORM:CSS*/' in s:
        s = re.sub(r'/\*FORM:CSS\*/.*?/\*/FORM:CSS\*/',
                   lambda _m: SELECT_CSS, s, flags=re.S)
    else:
        i = s.rindex('</style>')
        s = s[:i] + SELECT_CSS + '\n' + s[i:]

    open(p, 'w', encoding='utf-8').write(s)
    print('  form: the phone field shows the format it wants')
    return 0


if __name__ == '__main__':
    sys.exit(main())
