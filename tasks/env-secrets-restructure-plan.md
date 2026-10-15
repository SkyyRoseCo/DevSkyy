# `.env.secrets` restructure plan — 2026-09-21

**Contains no secret values. Line numbers + key names + disposition only.**
Execute in a FRESH session, AFTER credential rotation (see "Blocking" below).

Evidence: `dotenv_values()` / `dotenv.parser.parse_stream()` run against the file
this session `[repro]`. Hashes used for comparison, never values.

---

## Blocking — rotate first

On 2026-09-21 a redaction failure in this audit printed ~46 prose-parsed entries
(~30 recognizable live credentials) into a session transcript. See `bug-357` and
`tasks/lessons.md` → "names only is not redaction". **Do not restructure until
those are rotated**, or the work is done twice.

Rotate by provider: GitHub PAT ×4 · Anthropic ×1 · OpenAI-style ×1 · Google API
key ×2 · Google OAuth client id+secret · Google auth tokens ×2 · Pinecone ·
Docker Hub PAT · Figma PAT · Hugging Face · WooCommerce consumer key+secret ×2 ·
Replicate · Together.ai · Fal.ai · Threedium · Twilio SID · PostHog-style `papi.` ·
`sk_pr_default_` · `key_` · **a signed JWT with `"env":"production"` and exp 2030 —
long-lived, will not expire out of the problem.**

Rotating the two WooCommerce `ck_*` keys also closes backlog item #2 (the dashboard
and the Python API act on the store under different identities): the new pair must
land in BOTH `.env.wordpress` and `frontend/.env.local`.

---

## The two structural defects

| Line | Defect | Effect |
| ---- | ------ | ------ |
| 5 | closing quote is **U+201D** (curly `”`), not `"` | unterminated string |
| 233 | opens `"` and **never closes** | swallows to the next `"`, killing the 171–305 region |

Measured: **32 keys load before, 98 after the quote repair** — 66 new, of which
**20 are real env names and 46 are prose parsed as keys.** That 46 is the leak
vector: in this file the *key* side can be a secret.

---

## Disposition

### KEEP — load as-is, no conflict with any other env file

`4 SC_API_KEY` · `5 TRIPO_API_KEY` (fix the curly quote; drop the `export`) ·
`6 HF_TOKEN` · `85 ENCRYPTION_KEY` · `155 BYTEZ_MODEL_API_KEY` ·
`157 HUGGINGFACE_ACCESS_TOKEN` · `158 GROQ_API_KEY` · `160 LANGCHAIN_API_KEY` ·
`162 FASHN_API_KEY` · `163 WOOCOMMERCE_SECRET` · `165 WOOCOMMERCE_KEY` ·
`166 CONTEXT7_API_KEY` · `167 ARCADE__API` · `168 TRIPO3D_API_KEY` ·
`170 STRIPE_SECRET_ID` · `171 STRIPE_SECRET_KEY` · `200 REGISTRY` ·
`202 IMAGE_NAME` · `203 REGISTRY_USERNAME` · `204 REGISTRY_TOKEN` ·
`205 DEPLOY_MODE` · `207 SSH_USER` · `292 LANGFUSE_SECRET_KEY` ·
`294 LANGFUSE_PUBLIC_KEY` · `295 LANGFUSE_BASE_URL` · `313 STAGING_WORDPRESS_URL` ·
`316 HF_KEY`

Four of these are the "loads from nowhere" credentials the founder flagged and are
the whole point of the repair: **`HF_TOKEN`, `ENCRYPTION_KEY`, `STRIPE_SECRET_KEY`,
`REGISTRY_TOKEN`.** `HF_TOKEN` is a strict win — `.env` currently sets it to the
empty string, which is worse than missing (python-dotenv stores `""`, and that
blocks every later `override=False` load).

Founder decisions inside this group:

- `169 FASNH_API_KEY` — typo of `FASHN` and a duplicate of line 162. Probably delete.
- `167 ARCADE__API` — double underscore. Confirm the name consumers expect.
- `308 CONTEXT_DEV_API_KEY` — parses, but the value is empty. Keep or drop.

### DISABLE — comment out, each with the reason inline

These are the only four that would **change behavior**. Nothing else flips.

| Line | Key | Why disabled | Authoritative source |
| ---- | --- | ------------ | -------------------- |
| 79 | `OPENAI_API_KEY` | value is **744 chars** — several keys concatenated on one line | `.env.hf` (`config/settings.py:37`, override) |
| 183 | `ANTHROPIC_API_KEY` | value is **299 chars** — same concatenation defect | `.env` |
| 84 | `JWT_SECRET_KEY` | differs from `.env`; activating changes which key signs tokens — **every issued JWT invalid on restart** | `.env` |
| 206 | `SSH_HOST` | differs from `.env.wordpress`; equals the line-68 `URL` value, so activating points deploys at the wrong host | `.env.wordpress` |

### MOVE TO NOTEBOOK — not env assignments, must never parse

Destination: a file that is **not** named `.env.*` (nothing globs it into a
loader) and is gitignored — e.g. `.secrets-notebook.txt`. **Move verbatim, delete
nothing**; historical keys may still be needed.

| Lines | Content |
| ----- | ------- |
| 7–31, 33–66 | WP.com SFTP/SSH panel paste. Bare labels `SFTP`(32) `URL`(35,68) `PORT`(37,70) `USERNAME`(41,73) `PASSWORD`(45,76) `SSH`(52) parse as env keys under dangerously generic names |
| 81–153 | chronological credential paste log — prose labels containing `=` and `:` |
| 172–198 | Google OAuth / WooCommerce / Search Console / Pinecone / Cloudflare pastes |
| 208–290 | Auth0 / Repliers / Voyage / GitHub / Docker / Zencode / Grok / ReveAI / Bright Data pastes, plus a multi-line `curl -d '{...}'` example (259–274) whose braces produce bogus bindings |
| 296–311 | Claude long-lived token / Codex access token pastes |

Lines 68/70/73/76 carry the **real staging SFTP values** under the generic names
`URL`/`PORT`/`USERNAME`/`PASSWORD`. If those are needed as env vars they must be
re-added under explicit names (`STAGING_SFTP_*`). That is a founder decision —
do not invent the names.

---

## Regression gate to add with the fix

A test asserting `.env.secrets` parses with **zero** `could not parse` warnings and
that every resulting key matches `^[A-Z][A-Z0-9_]*$`. That second assertion is the
one that would have caught this class: a key not matching that pattern means a
secret is sitting on the key side. Fail closed — absent file blocks, never passes.
