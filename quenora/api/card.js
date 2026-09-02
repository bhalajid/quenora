/* ═══════════════════════════════════════════════════════════════════
   GET /c  —  what the contact QR opens.

   Two jobs, in this order:

     1  count the scan
     2  hand over the vCard

   WHAT IS COUNTED, AND WHAT IS NOT

   A count, a code and a day. That is the whole record:

       { "card": 14, "event": 3 }   per day

   No IP, no user agent, no cookie, no fingerprint, nothing that identifies a
   person or a device. That is not caution for its own sake — the privacy
   notice on this site says it sets no cookies and does not track, and that
   sentence is worth more than knowing which city a scan came from. A QR code
   cannot tell you who scanned it in any case; it can only tell you that
   somebody did, and which printed run they were holding.

   WHERE THE COUNT LIVES

   Vercel functions are stateless, so the count needs somewhere to go. If
   Upstash/Vercel KV is configured it increments a key there. If it is not,
   the scan is written to the function log and the card still works — the same
   trade api/enquiry.js makes: degrade honestly rather than fail silently.

     KV_REST_API_URL     from Vercel KV or Upstash
     KV_REST_API_TOKEN

   READING THE COUNT

     GET /c?stats=1      returns the per-day totals as JSON
   ═══════════════════════════════════════════════════════════════════ */

const CARD = {
  org:   'Quenora Consulting',
  role:  'Enterprise AI & automation',
  tel:   ['+4915233927436', '+4915256433329'],
  email: 'info@quenora.ai',
  url:   'https://quenora.ai',
  city:  'Heilbronn',
  country: 'Germany'
};

/* vCard 3.0 — the version every phone reads. 4.0 is newer and Android's
   importer is still uneven with it, which is the wrong place to be modern. */
function vcard() {
  const lines = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    /* FN is what the phone files it under. The company name, not a person's,
       because that is the name someone will search for afterwards. */
    'FN:' + CARD.org,
    'N:' + CARD.org + ';;;;',
    'ORG:' + CARD.org,
    'TITLE:' + CARD.role,
    'TEL;TYPE=CELL,VOICE:' + CARD.tel[0],
    'TEL;TYPE=WORK,VOICE:' + CARD.tel[1],
    'EMAIL;TYPE=INTERNET,WORK:' + CARD.email,
    'URL:' + CARD.url,
    'ADR;TYPE=WORK:;;;' + CARD.city + ';;;' + CARD.country,
    'NOTE:We engineer AI into the systems you already run, then hand it over.',
    'END:VCARD'
  ];
  /* CRLF is required by RFC 6350; some Android importers reject LF-only */
  return lines.join('\r\n') + '\r\n';
}

function today() { return new Date().toISOString().slice(0, 10); }

async function kv(path, method) {
  const base = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!base || !token) return null;
  try {
    const r = await fetch(base + path, {
      method: method || 'GET',
      headers: { Authorization: 'Bearer ' + token }
    });
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}

async function count(code) {
  const key = 'qr:' + today() + ':' + code;
  const done = await kv('/incr/' + encodeURIComponent(key));
  if (done) return true;
  /* No store configured. The scan still happened and the card still works —
     say so in the log rather than pretending it was recorded. */
  console.log(JSON.stringify({ scan: code, day: today(), stored: false }));
  return false;
}

async function stats() {
  const keys = await kv('/keys/' + encodeURIComponent('qr:*'));
  if (!keys || !Array.isArray(keys.result)) return null;
  const out = {};
  for (const k of keys.result) {
    const v = await kv('/get/' + encodeURIComponent(k));
    const parts = k.split(':');           /* qr : day : code */
    if (!v || parts.length < 3) continue;
    out[parts[1]] = out[parts[1]] || {};
    out[parts[1]][parts[2]] = Number(v.result) || 0;
  }
  return out;
}

export default async function handler(req, res) {
  const url = new URL(req.url, 'https://quenora.ai');

  if (url.searchParams.get('stats') === '1') {
    const s = await stats();
    res.setHeader('Cache-Control', 'no-store');
    return s
      ? res.status(200).json({ ok: true, scans: s })
      : res.status(503).json({
          ok: false, configured: false,
          error: 'No scan store configured. Set KV_REST_API_URL and '
               + 'KV_REST_API_TOKEN, or read the counts from the function log.'
        });
  }

  /* the printed run, if the code carries one; letters and digits only, so a
     crafted URL cannot write arbitrary keys */
  const raw = (url.searchParams.get('k') || 'site').toLowerCase();
  const code = /^[a-z0-9-]{1,24}$/.test(raw) ? raw : 'site';
  await count(code);

  res.setHeader('Content-Type', 'text/vcard; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename="quenora.vcf"');
  res.setHeader('Cache-Control', 'no-store');
  return res.status(200).send(vcard());
}
