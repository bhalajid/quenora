/* ═══════════════════════════════════════════════════════════════════
   GET /w  —  Save Quenora Consulting to a phone's wallet.

   WHY A WALLET PASS AT ALL, WHEN /c ALREADY SAVES A CONTACT

   A vCard lands in Contacts, which is where a phone number belongs and
   where someone will look for it in eight months. A wallet pass is a
   different thing: it is a card in a stack of cards, it survives a phone
   migration, and — the only reason it is worth building — it can be
   updated after it has been handed over. Change a number, and every pass
   that was ever saved changes with it. Paper cannot do that.

   So this is not a replacement for /c. It is the second half: the vCard
   for the address book, the pass for the wallet. Both from one scan.

   APPLE VS GOOGLE — AN HONEST DIFFERENCE

   Google Wallet needs a Google Cloud service account and an issuer ID,
   both free. That is implemented here, in full.

   Apple Wallet needs a .pkpass: a zip whose manifest is signed with a
   PKCS#7 detached signature from an Apple Pass Type ID certificate. That
   certificate requires a paid Apple Developer Program membership, and
   PKCS#7 detached signing is not in Node's crypto module — it needs a
   signing dependency this site does not have and, being zero-dependency
   by design, does not want lightly. Apple is therefore NOT implemented.
   It is one file and an afternoon once the certificate exists; see
   LAUNCH.md. Nothing here pretends otherwise, and the button below does
   not appear for a wallet that is not configured.

   THE SAME RULE AS /c

   The pass carries the company's details outward. It carries nothing
   about the person holding it back. There is no tracking in a saved
   pass beyond the fact that a save link was requested — counted the same
   way a scan is, by day and by code, with no IP and no user agent.
   ═══════════════════════════════════════════════════════════════════ */

import crypto from 'node:crypto';

const CARD = {
  org:   'Quenora Consulting',
  role:  'Enterprise AI & automation',
  tel:   ['+4915233927436', '+4915256433329'],
  email: 'info@quenora.ai',
  url:   'https://quenora.ai',
  city:  'Heilbronn',
  country: 'Germany'
};

/* ── the same count as /c, so both halves of one scan land in one place ── */
async function count(code) {
  const base = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN;
  const day = new Date().toISOString().slice(0, 10);
  if (!base || !tok) {
    console.log(JSON.stringify({ wallet: code, day, stored: false }));
    return;
  }
  try {
    await fetch(`${base}/hincrby/quenora:wallet:${day}/${code}/1`,
                { headers: { Authorization: `Bearer ${tok}` } });
    console.log(JSON.stringify({ wallet: code, day, stored: true }));
  } catch (e) {
    /* a store that is down must never cost someone their contact card */
    console.log(JSON.stringify({ wallet: code, day, stored: false,
                                 error: String(e && e.message || e) }));
  }
}

/* ── base64url, which JWT needs and Buffer does not spell the same way ── */
const b64u = b => Buffer.from(b).toString('base64')
  .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

/* ── the Google Wallet save link ──────────────────────────────────────
   The class and the object both travel inside the JWT, so there is no
   provisioning call to make and no state to keep in sync. Google reads
   the class from the token the first time and the object every time. */
function googleSaveUrl() {
  const issuer = process.env.GOOGLE_WALLET_ISSUER_ID;
  const rawKey = process.env.GOOGLE_WALLET_SA_KEY;
  const email  = process.env.GOOGLE_WALLET_SA_EMAIL;
  if (!issuer || !rawKey || !email) return null;

  /* env vars cannot hold real newlines in most dashboards, so the PEM is
     usually pasted with literal \n. Accept either form. */
  const key = rawKey.includes('-----BEGIN')
    ? rawKey.replace(/\\n/g, '\n')
    : Buffer.from(rawKey, 'base64').toString('utf8');

  const classId  = `${issuer}.quenora_contact`;
  const objectId = `${issuer}.quenora_contact_v1`;

  const genericClass = {
    id: classId,
    classTemplateInfo: {
      cardTemplateOverride: {
        cardRowTemplateInfos: [{
          twoItems: {
            startItem: { firstValue: { fields: [
              { fieldPath: "object.textModulesData['tel1']" }] } },
            endItem:   { firstValue: { fields: [
              { fieldPath: "object.textModulesData['tel2']" }] } }
          }
        }]
      }
    }
  };

  const genericObject = {
    id: objectId,
    classId,
    /* hexBackgroundColor is the void the rest of the site is painted in */
    hexBackgroundColor: '#07070a',
    cardTitle:  { defaultValue: { language: 'en', value: CARD.org } },
    header:     { defaultValue: { language: 'en', value: CARD.role } },
    subheader:  { defaultValue: { language: 'en',
                                  value: `${CARD.city}, ${CARD.country}` } },
    textModulesData: [
      { id: 'tel1',  header: 'Phone',  body: CARD.tel[0] },
      { id: 'tel2',  header: 'Mobile', body: CARD.tel[1] },
      { id: 'email', header: 'Email',  body: CARD.email }
    ],
    linksModuleData: {
      uris: [
        { uri: CARD.url,                    description: 'quenora.ai',      id: 'site' },
        { uri: `mailto:${CARD.email}`,      description: CARD.email,        id: 'mail' },
        { uri: `tel:${CARD.tel[0]}`,        description: 'Call',            id: 'call' },
        { uri: `${CARD.url}/c`,             description: 'Save to Contacts', id: 'vcf' }
      ]
    },
    barcode: { type: 'QR_CODE', value: `${CARD.url}/c?k=wallet`,
               alternateText: 'quenora.ai' }
  };

  const claims = {
    iss: email,
    aud: 'google',
    typ: 'savetowallet',
    iat: Math.floor(Date.now() / 1000),
    origins: ['https://quenora.ai'],
    payload: { genericClasses: [genericClass], genericObjects: [genericObject] }
  };

  const head = b64u(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const body = b64u(JSON.stringify(claims));
  const sig  = b64u(crypto.sign('RSA-SHA256', Buffer.from(`${head}.${body}`), key));
  return `https://pay.google.com/gp/v/save/${head}.${body}.${sig}`;
}

export default async function handler(req, res) {
  const url = new URL(req.url, 'https://quenora.ai');
  res.setHeader('Cache-Control', 'no-store');

  /* the page asks this before it decides whether to draw a button; a button
     that leads to a 503 is worse than no button */
  if (url.searchParams.get('probe') === '1') {
    return res.status(200).json({ google: !!googleSaveUrl(), apple: false });
  }

  const raw  = (url.searchParams.get('k') || 'site').toLowerCase();
  const code = /^[a-z0-9-]{1,24}$/.test(raw) ? raw : 'site';

  const link = googleSaveUrl();
  if (!link) {
    /* no wallet configured — hand over the thing that always works */
    return res.status(302)
      .setHeader('Location', `/c?k=${encodeURIComponent(code)}`)
      .end();
  }
  await count(code);
  return res.status(302).setHeader('Location', link).end();
}
