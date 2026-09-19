export const meta = {
  name: 'self-healing-theme-loop',
  description:
    'Autonomous self-healing + self-improving + learning loop for the SkyyRose WordPress theme. ' +
    'Runs every 6h via cron. Monitors skyyrose.co (S1/S2/S3/S4), detects regressions against baseline, ' +
    'learns from heal-knowledge.json (LEARN-FIRST), heals root causes in a git worktree with a code-review ' +
    'net-improvement gate, optionally deploys (AUTO_DEPLOY=true only), and writes all outcomes back to the ' +
    'knowledge store and heal log for ML-ready accumulation. Zero I/O or time/random APIs in the script — ' +
    'every shell call, timestamp, and file write happens inside an agent.',
  phases: [
    { title: 'Monitor',       detail: 'Agent runs S1/S2/S3 via cache-busted curl, S4 best-effort MCP; returns structured signals' },
    { title: 'Diagnose',      detail: 'Reads baseline + heal-knowledge.json; computes regressions; applies LEARN-FIRST (known signature → proven fix)' },
    { title: 'Heal+Improve',  detail: 'Per-surface heal-doctor agent in git worktree; code-review gate judging heal AND net-improvement (1 root-cause retry)' },
    { title: 'Gate',          detail: 'php -l on touched PHP + phpcs (V1 --standard=.phpcs.xml, V2 --standard=phpcs.xml; errors) + best-effort Playwright harness' },
    { title: 'Deploy',        detail: 'Hard-gated on args.autoDeploy===true AND gate green AND settings permission; else dry manifest' },
    { title: 'Learn-after',   detail: 'Upsert heal-knowledge.json, append heal-log.jsonl, surface escalations, update .wolf/memory.md' },
  ],
}

// ---------------------------------------------------------------- canonical paths

const REPO      = '/Users/theceo/DevSkyy'
// Two themes exist. THEME is the V1 source this loop was built against ("SkyyRose", text domain
// skyyrose, SKYYROSE_VERSION). skyyrose.co serves the "SkyyRose Flagship 2" lineage (text domain
// skyyrose-flagship-2, SKYYROSE2_VERSION), whose source is THEME_V2. Prompts name both so the heal
// doctor states which theme it edits instead of assuming "the theme" is V1.
const THEME     = `${REPO}/wordpress-theme/skyyrose-flagship`
const THEME_V2  = `${REPO}/wordpress-theme/skyyrose-flagship-2`
const THEME_NOTE =
  'V1 "SkyyRose" (text domain skyyrose, SKYYROSE_VERSION). NOTE: skyyrose.co serves the "SkyyRose Flagship 2" ' +
  'lineage (text domain skyyrose-flagship-2, SKYYROSE2_VERSION, own package.json; build: npm run build:assets) ' +
  'whose source is Theme V2 below — read the live style.css Theme Name/Text Domain and state which theme you edit.'
const BASELINE  = `${REPO}/.claude/state/theme-health-baseline.json`
const KNOWLEDGE = `${REPO}/.claude/state/heal-knowledge.json`
const HEAL_LOG  = `${REPO}/tasks/heal-log.jsonl`
const WOLF_MEM  = `${REPO}/.wolf/memory.md`
const DEPLOY_SH = `${REPO}/scripts/deploy-theme.sh`
const BASE_URL  = 'https://skyyrose.co'

// ---------------------------------------------------------------- schemas (flat + typed — ML-ready)

const MONITOR_SCHEMA = {
  type: 'object',
  required: ['ts', 'cbParam', 's1Pages', 's2Canon', 's3Asset', 's4Advisory'],
  properties: {
    ts:         { type: 'string', description: 'ISO timestamp from shell: date -u +%FT%TZ' },
    cbParam:    { type: 'string', description: 'Cache-bust value from shell: date +%s' },
    s1Pages: {
      type: 'array',
      items: {
        type: 'object',
        required: ['path', 'http', 'sizeKB', 'phpError', 'ok'],
        properties: {
          path:     { type: 'string' },
          http:     { type: 'number' },
          sizeKB:   { type: 'number' },
          phpError: { type: 'boolean' },
          ok:       { type: 'boolean', description: 'true = passes baseline; false = regression' },
          detail:   { type: 'string' },
        },
      },
    },
    s2Canon: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'ok', 'observed'],
        properties: {
          id:       { type: 'string' },
          ok:       { type: 'boolean' },
          observed: { type: 'boolean', description: 'Whether the grep pattern was found in live HTML' },
          detail:   { type: 'string' },
        },
      },
    },
    s3Asset: {
      type: 'object',
      required: ['ok', 'assetVersionFound', 'assetsReturning200'],
      properties: {
        ok:                 { type: 'boolean' },
        assetVersionFound:  { type: 'string' },
        assetsReturning200: { type: 'array', items: { type: 'string' } },
        detail:             { type: 'string' },
      },
    },
    s4Advisory: {
      type: 'object',
      required: ['available', 'ok'],
      properties: {
        available:      { type: 'boolean', description: 'false = MCP unavailable headless; skip-with-log' },
        ok:             { type: 'boolean' },
        perfScore:      { type: 'number' },
        a11yScore:      { type: 'number' },
        consoleErrors:  { type: 'array', items: { type: 'string' } },
        detail:         { type: 'string' },
      },
    },
  },
}

const DIAGNOSE_SCHEMA = {
  type: 'object',
  required: ['cycle', 'regressions', 'knownSignatures', 'escalations'],
  properties: {
    cycle:       { type: 'number', description: 'Incremented baseline.cycles + 1' },
    regressions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['signature', 'surface', 'severity', 'signal', 'description', 'knownFix'],
        properties: {
          signature:    { type: 'string', description: 'Stable key: e.g. s1:/:http:404' },
          surface:      { type: 'string', description: 'Which file/template surface is affected' },
          severity:     { type: 'string', enum: ['critical', 'high', 'medium'] },
          signal:       { type: 'string', enum: ['s1', 's2', 's3', 's4'] },
          description:  { type: 'string' },
          knownFix:     { type: 'boolean', description: 'Signature matched heal-knowledge.json' },
          fixPattern:   { type: 'string', description: 'If knownFix=true, the proven pattern from heal-knowledge' },
          recurrences:  { type: 'number', description: 'How many times this signature has appeared before' },
          shouldEscalate: { type: 'boolean', description: 'true if recurrences>=2 AND prior fix only treated symptom' },
        },
      },
    },
    knownSignatures:  { type: 'array', items: { type: 'string' } },
    escalations:      { type: 'array', items: { type: 'string' }, description: 'Signatures that failed healing >=2 consecutive cycles and must NOT be healed again — only escalated' },
    clean:            { type: 'boolean', description: 'true = no regressions, site is healthy' },
  },
}

const HEAL_SCHEMA = {
  type: 'object',
  required: ['signature', 'surface', 'healed', 'isNetImprovement', 'filesChanged', 'summary', 'rootCauseFix', 'preventionAdded'],
  properties: {
    signature:          { type: 'string' },
    surface:            { type: 'string' },
    healed:             { type: 'boolean', description: 'Regression is resolved in the worktree. Set false only when fix was attempted but failed. Set true when verdict is false-positive (nothing to fix — regression does not exist).' },
    falsePositive:      { type: 'boolean', description: 'true = live state and source both agree the regression signal was spurious; no fix needed. When falsePositive=true, healed must also be true.' },
    falsePositiveReason: { type: 'string', description: 'Explanation of why this is a false positive' },
    isNetImprovement:   { type: 'boolean', description: 'Code is objectively better, not just patched. Set true when falsePositive=true (no code change = no regression).' },
    filesChanged:       { type: 'array', items: { type: 'string' } },
    summary:            { type: 'string' },
    rootCauseFix:       { type: 'string', description: 'What root cause was addressed so the bug class cannot recur' },
    preventionAdded:    { type: 'string', description: 'Permanent guard, new assertion, or new monitor signal added' },
    minRebuilt:         { type: 'boolean' },
    worktreePath:       { type: 'string' },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['signature', 'healConfirmed', 'netImprovementConfirmed', 'sendBackForRootCause', 'verifyOutput'],
  properties: {
    signature:                { type: 'string' },
    healConfirmed:            { type: 'boolean' },
    netImprovementConfirmed:  { type: 'boolean' },
    sendBackForRootCause:     { type: 'boolean', description: 'true = merely patched, doctor must retry root-cause pass' },
    verifyOutput:             { type: 'string', description: 'Actual output from php -l / phpcs / visual grep' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'issue'],
        properties: {
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          file:     { type: 'string' },
          issue:    { type: 'string' },
        },
      },
    },
  },
}

const GATE_SCHEMA = {
  type: 'object',
  required: ['pass', 'phpLintPass', 'phpcsPass', 'playwrightPass', 'checks'],
  properties: {
    pass:           { type: 'boolean' },
    phpLintPass:    { type: 'boolean' },
    phpcsPass:      { type: 'boolean' },
    playwrightPass: { type: 'boolean', description: 'best-effort; null if harness unavailable' },
    checks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'status'],
        properties: {
          name:   { type: 'string' },
          status: { type: 'string', enum: ['pass', 'warn', 'fail', 'skip'] },
          detail: { type: 'string' },
        },
      },
    },
  },
}

const DEPLOY_SCHEMA = {
  type: 'object',
  required: ['attempted', 'deployed', 'dry', 'manifest'],
  properties: {
    attempted: { type: 'boolean' },
    deployed:  { type: 'boolean' },
    dry:       { type: 'boolean' },
    manifest:  { type: 'string', description: 'What would have deployed (or did deploy)' },
    detail:    { type: 'string' },
  },
}

const LEARN_SCHEMA = {
  type: 'object',
  required: ['cycle', 'knowledgeUpdated', 'healLogAppended', 'wolfMemUpdated', 'lessons', 'mineFindings'],
  properties: {
    cycle:              { type: 'number' },
    knowledgeUpdated:   { type: 'array', items: { type: 'string' }, description: 'Signatures upserted into heal-knowledge.json' },
    healLogAppended:    { type: 'boolean' },
    wolfMemUpdated:     { type: 'boolean' },
    lessons:            { type: 'array', items: { type: 'string' } },
    mineFindings: {
      type: 'array',
      description: 'Signatures with recurrences>=3 that need structural fix proposals',
      items: {
        type: 'object',
        required: ['signature', 'recurrences', 'proposedStructuralFix'],
        properties: {
          signature:              { type: 'string' },
          recurrences:            { type: 'number' },
          proposedStructuralFix:  { type: 'string' },
          proposedNewSignal:      { type: 'string' },
        },
      },
    },
  },
}

// ---------------------------------------------------------------- main

// No args.task check — this is cron-triggered, headless. Runs unconditionally.
const autoDeploy = !!(args && args.autoDeploy === true)

// ================================================================
// PHASE 1 — MONITOR
// ================================================================
phase('Monitor')

const monitorResult = await agent(
  `You are the SITE MONITOR agent for the SkyyRose WordPress theme self-healing loop.

Your job: run all monitor signals against https://skyyrose.co and return structured results.
Do NOT deploy, edit files, or modify anything — READ-ONLY.

BASELINE file: ${BASELINE}
KNOWLEDGE file: ${KNOWLEDGE}

STEP 0 — Get timestamps (shell, not JS):
Run: date -u +%FT%TZ    → use as "ts"
Run: date +%s           → use as "cbParam" (append as ?cb=VALUE to all curl URLs)

STEP 1 — S1: HTTP + size + PHP-error check (curl, no MCP needed)
For each page in baseline.pages, run:
  curl -s -o /tmp/sr_page_<slug>.html -w "%{http_code} %{size_download}" "https://skyyrose.co<path>?cb=$cbParam"
Check:
  - HTTP status matches baseline.expectedHttp (200 for pages, 404 for the sentinel)
  - Downloaded size in bytes >= baseline.sizeFloorKB * 1024
  - Body does NOT contain: "Fatal error" | "Parse error" | "Call to undefined" | "There has been a critical error"
ok = all three pass. If any fail, ok=false and set detail with which check failed.
Store raw bytes → convert to KB (2 decimal places) in sizeKB.

STEP 2 — S2: Canon-drift check (grep live HTML)
For each entry in baseline.canonChecks, re-use the already-fetched HTML (/tmp/sr_page_<slug>.html for matching path):
  - grep for the "grep" string (case-sensitive)
  - observed = whether the pattern was found in the HTML
  - ok = (observed === expectedPresent)
  - detail any mismatch

STEP 3 — S3: Asset version + .min asset availability
From the homepage HTML already fetched:
  - grep for ?ver= strings on theme CSS/JS assets (assets/css or assets/js in the URL)
  - assetVersionFound = most common theme ?ver= value seen
  - ok = (assetVersionFound === baseline.assetVersion) AND all .min assets in baseline.assetChecks return HTTP 200
    Run: curl -s -o /dev/null -w "%{http_code}" "<assetCheck.url>" for each assetCheck entry

STEP 4 — S4: Best-effort Lighthouse + console (MCP chrome-devtools)
Try to run a Lighthouse audit on https://skyyrose.co and collect console errors.
If the MCP tool is unavailable (headless environment, no browser), set available=false, ok=true, and log "S4 skipped — headless" in detail.
NEVER fail the overall cycle on S4 alone. S4 is advisory.

Return the MONITOR_SCHEMA object. All fields required. Be precise — every number must be real, not estimated.`,
  { schema: MONITOR_SCHEMA, label: 'monitor', phase: 'Monitor' },
)

log(`Monitor complete. ts=${monitorResult.ts}, cbParam=${monitorResult.cbParam}`)

const s1Failures = (monitorResult.s1Pages || []).filter(p => !p.ok)
const s2Failures = (monitorResult.s2Canon || []).filter(c => !c.ok)
const s3Ok       = monitorResult.s3Asset && monitorResult.s3Asset.ok
const s4Ok       = !monitorResult.s4Advisory || !monitorResult.s4Advisory.available || monitorResult.s4Advisory.ok

const hasRegressions = s1Failures.length > 0 || s2Failures.length > 0 || !s3Ok

log(`S1: ${s1Failures.length} page failures | S2: ${s2Failures.length} canon failures | S3: ${s3Ok ? 'ok' : 'FAIL'} | S4 advisory: ${s4Ok ? 'ok' : 'issues (non-blocking)'}`)

// ================================================================
// PHASE 2 — DIAGNOSE
// ================================================================
phase('Diagnose')

const diagnoseResult = await agent(
  `You are the DIAGNOSE agent for the SkyyRose theme self-healing loop.

Read these files IN FULL before proceeding:
  Baseline : ${BASELINE}
  Knowledge: ${KNOWLEDGE}

MONITOR SIGNALS (from this cycle):
${JSON.stringify({ s1Failures, s2Failures, s3Ok, s4Ok, s4Detail: monitorResult.s4Advisory }, null, 2)}

FULL monitor output:
${JSON.stringify(monitorResult, null, 2)}

YOUR TASKS:

1. Compute cycle number: read "cycles" from heal-knowledge.json and add 1.

2. For each monitor failure (S1, S2, S3 — S4 is advisory only), produce a regression entry:
   - signature: stable machine key, format "<signal>:<path>:<check-type>" e.g. "s1:/shop/:size" or "s2:/:home-tagline"
   - surface: the PHP template or CSS/JS file most likely responsible (read CLAUDE.md learnings + anatomy.md if helpful)
   - severity: page-down or php-error → "critical"; canon-drift or asset miss → "high"; S4-only → "medium"
   - signal: "s1" | "s2" | "s3" | "s4"
   - description: human-readable what failed
   - knownFix: does this signature appear in heal-knowledge.json signatures[]?
   - fixPattern: if knownFix=true, copy the proven fixPattern string from knowledge
   - recurrences: how many times this signature has appeared (from knowledge, 0 if new)
   - shouldEscalate: recurrences >= 2 AND prior lastOutcome was NOT "healed" — means symptom-patch failed, need root-cause

3. List escalations: signatures that must NOT be healed again (healFailedConsecutive >= 2 in knowledge).
   These go to the log only — the Heal phase SKIPS them.

4. Set clean=true if and only if regressions array is empty.

5. LEARN-FIRST rule: for any regression with knownFix=true, the Heal phase MUST use that fixPattern as the starting point.
   For any regression with recurrences >= 2, the Heal phase MUST address the root cause, not the symptom.

Return the DIAGNOSE_SCHEMA object. Be precise. Every regression needs a signature.`,
  { schema: DIAGNOSE_SCHEMA, label: 'diagnose', phase: 'Diagnose' },
)

log(`Diagnose: cycle=${diagnoseResult.cycle}, regressions=${diagnoseResult.regressions.length}, escalations=${diagnoseResult.escalations.length}, clean=${diagnoseResult.clean}`)

// No regressions → skip Heal+Improve and Gate; still run Learn-after
const regressions      = diagnoseResult.regressions || []
const escalations      = diagnoseResult.escalations || []
const actionableRegs   = regressions.filter(r => !escalations.includes(r.signature))

let healResults = []
let gateResult  = null
let deployResult = null

if (actionableRegs.length > 0) {
  // ================================================================
  // PHASE 3 — HEAL + IMPROVE (per surface, with code-review gate)
  // ================================================================
  phase('Heal+Improve')

  healResults = await pipeline(
    actionableRegs,

    // Stage A — heal-doctor does the fix in a worktree
    (reg, _orig, i) =>
      agent(
        `You are the theme-heal-doctor. Heal regression ${i + 1}/${actionableRegs.length}.

REGRESSION:
${JSON.stringify(reg, null, 2)}

KEY PATHS:
  Repo  : ${REPO}
  Theme : ${THEME}  — ${THEME_NOTE}
  Theme V2 : ${THEME_V2}
  Baseline : ${BASELINE}
  Knowledge: ${KNOWLEDGE}

Read the heal-doctor agent definition at ${REPO}/.claude/agents/theme-heal-doctor.md for full instructions.
Follow every step exactly. Create a git worktree off HEAD for your changes.
Source timestamp for branch name: run shell \`date +%s\`.

Your fix MUST:
  (a) Restore the broken feature — verified against baseline expectations.
  (b) Fix the ROOT CAUSE so this bug class cannot recur (especially if recurrences >= 2).
  (c) Leave the touched code better: dedup, add guard/early-return/assert, tighten escaping, remove dead refs.
      BOUNDED to the touched surface — no sprawling refactors.
  (d) For any CSS/JS source edit: run \`node ${REPO}/scripts/build-css.js && node ${REPO}/scripts/build-js.js\` to rebuild .min files.
  (e) No innerHTML in JS. Escape all PHP output (esc_html, esc_attr, esc_url, wp_kses_post). $wpdb->prepare always.
  (f) If knownFix is provided, START from that fixPattern: ${reg.knownFix ? reg.fixPattern : '(none — new signature)'}

Return the HEAL_SCHEMA object with exact file paths, rootCauseFix, and preventionAdded.`,
        { agentType: 'theme-heal-doctor', schema: HEAL_SCHEMA, label: `heal:${reg.signature}:${i}`, phase: 'Heal+Improve', isolation: 'worktree' },
      ),

    // Stage B — code-review gate: heals AND net-improvement? One root-cause retry if merely patched.
    async (healAttempt, reg, i) => {
      if (!healAttempt) {
        return { reg, healAttempt, review: null, finalHealed: false, needsEscalate: true }
      }
      // False-positive path: doctor confirmed the regression signal was spurious — no fix needed.
      // Log it as healed (nothing broken), no escalation, no deploy trigger.
      if (healAttempt.falsePositive === true) {
        return { reg, healAttempt, review: null, finalHealed: true, needsEscalate: false, falsePositive: true }
      }
      if (!healAttempt.healed) {
        return { reg, healAttempt, review: null, finalHealed: false, needsEscalate: true }
      }

      let review = null
      // Up to 2 attempts: initial review, then one root-cause retry
      for (let attempt = 1; attempt <= 2; attempt++) {
        review = await agent(
          `You are the CODE REVIEWER for the self-healing loop (attempt ${attempt}/2).

Review the heal applied to signature: ${reg.signature}

Heal summary  : ${healAttempt.summary}
Root cause fix: ${healAttempt.rootCauseFix}
Files changed : ${(healAttempt.filesChanged || []).join(', ')}
Worktree path : ${healAttempt.worktreePath || '(not specified)'}

Judge on TWO axes — both must be true for the review to pass:
  1. HEALS: The regression is resolved. Run php -l via /opt/homebrew/bin/php on touched PHP files. Grep live-ish source for the expected canon string. Verify the fix addresses the baseline check that failed.
  2. NET-IMPROVEMENT: The touched code is objectively better than before — root cause removed, guard added, dead code pruned, escaping tightened — NOT just a surface patch that re-opens next cycle.

If healConfirmed=true AND netImprovementConfirmed=true → done.
If healConfirmed=true BUT netImprovementConfirmed=false (merely patched):
  - On attempt 1: set sendBackForRootCause=true; the doctor will get one more pass.
  - On attempt 2: accept, but flag in findings with severity=high.
If healConfirmed=false: set healConfirmed=false; this will trigger escalation.

Put REAL verify output (command + result) in verifyOutput. Do not fabricate.`,
          { agentType: 'code-reviewer', schema: REVIEW_SCHEMA, label: `review:${reg.signature}:a${attempt}`, phase: 'Heal+Improve' },
        )
        // If merely patched on attempt 1, do a root-cause retry by re-running the heal agent
        if (review && review.sendBackForRootCause && attempt === 1) {
          healAttempt = await agent(
            `ROOT-CAUSE RETRY for signature: ${reg.signature}

The code reviewer found your fix healed the symptom but did not address the root cause. One retry is permitted.

Original heal summary: ${healAttempt.summary}
Reviewer comment: ${JSON.stringify(review.findings || [])}

Requirements for this retry:
  - Fix the ROOT CAUSE so this regression class cannot recur.
  - The fix must be a structural improvement, not an incremental patch.
  - Do NOT re-open the worktree — apply on top of your existing worktree changes.
  - Rebuild .min files if CSS/JS touched.
  - Update rootCauseFix and preventionAdded in your response to reflect the new approach.

Return HEAL_SCHEMA.`,
            { agentType: 'theme-heal-doctor', schema: HEAL_SCHEMA, label: `heal:${reg.signature}:retry`, phase: 'Heal+Improve', isolation: 'worktree' },
          )
          continue // proceed to attempt 2 review
        }
        break // clean pass or attempt 2 done
      }

      const finalHealed    = !!(review && review.healConfirmed)
      const needsEscalate  = !finalHealed
      return { reg, healAttempt, review, finalHealed, needsEscalate }
    },
  )

  const healedCount    = healResults.filter(r => r && r.finalHealed).length
  const escalatedCount = healResults.filter(r => r && r.needsEscalate).length
  log(`Heal+Improve: ${healedCount}/${actionableRegs.length} healed; ${escalatedCount} escalated`)

  // ================================================================
  // PHASE 4 — GATE
  // ================================================================
  phase('Gate')

  const healedSurfaces = healResults
    .filter(r => r && r.finalHealed && r.healAttempt)
    .flatMap(r => r.healAttempt.filesChanged || [])

  if (healedSurfaces.length === 0) {
    log('Gate: no healed surfaces — skipping gate, treating as pass (nothing to gate).')
    gateResult = {
      pass: true,
      phpLintPass: true,
      phpcsPass: true,
      playwrightPass: true,
      checks: [{ name: 'no-healed-surfaces', status: 'skip', detail: 'No files were changed' }],
    }
  } else {
    gateResult = await agent(
      `You are the GATE agent for the self-healing loop.

Verify the heal changes are safe to deploy. Run ALL checks — report real output, not assumptions.

FILES CHANGED by heal:
${healedSurfaces.join('\n')}

THEME ROOT: ${THEME}  — ${THEME_NOTE}
THEME V2 ROOT: ${THEME_V2}  (use this root for the checks when the heal edited V2 files)

CHECKS REQUIRED:

1. PHP LINT (php -l) — run via /opt/homebrew/bin/php
   For each changed .php file: /opt/homebrew/bin/php -l <file>
   phpLintPass = all return "No syntax errors detected"

2. PHPCS — errors only (each theme has its own ruleset: V1 .phpcs.xml, V2 phpcs.xml; never apply one theme's standard to the other)
   V1: cd ${THEME} && vendor/bin/phpcs --standard=.phpcs.xml -s --report=summary <changed php files>
   (Composer must be installed: ~/.local/bin/composer install if vendor/ missing)
   V2: cd ${THEME_V2} && ${THEME}/vendor/bin/phpcs --standard=phpcs.xml -s --report=summary <changed php files>
   (skyyrose-flagship-2 has no vendor/; the V1 theme's composer install supplies the binary)
   phpcsPass = zero errors (warnings ok)

3. PLAYWRIGHT — best-effort
   If a Playwright harness exists at ${REPO} (check for playwright.config.*), run: npx playwright test --reporter=line
   If unavailable, set playwrightPass=true and status=skip.

4. SOURCE/MIN DRIFT check
   If any .css or .js file was changed: verify corresponding .min file was also regenerated
   (check mtime or grep for the same distinctive token in both source and .min)

Gate pass = phpLintPass AND phpcsPass (playwright is advisory; source/min drift = warn not fail).
Return GATE_SCHEMA. Include real command output in each check's detail field.`,
      { schema: GATE_SCHEMA, label: 'gate', phase: 'Gate' },
    )
    log(`Gate: pass=${gateResult.pass}, phpLint=${gateResult.phpLintPass}, phpcs=${gateResult.phpcsPass}, playwright=${gateResult.playwrightPass}`)
  }

  // ================================================================
  // PHASE 5 — DEPLOY (hard-gated)
  // ================================================================
  phase('Deploy')

  const gateGreen = !!(gateResult && gateResult.pass)

  if (!autoDeploy) {
    log('Deploy: autoDeploy=false — dry run. Manifest will be written to heal log.')
    deployResult = {
      attempted: false,
      deployed: false,
      dry: true,
      manifest: `DRY — gate=${gateGreen ? 'GREEN' : 'RED'}, autoDeploy=false. Files that WOULD deploy: ${healedSurfaces.join(', ') || 'none'}`,
      detail: 'Set args.autoDeploy=true AND env AUTO_DEPLOY=true to enable real deploys.',
    }
  } else if (!gateGreen) {
    log('Deploy: gate RED — not deploying.')
    deployResult = {
      attempted: false,
      deployed: false,
      dry: true,
      manifest: `BLOCKED — gate RED. phpLint=${gateResult.phpLintPass}, phpcs=${gateResult.phpcsPass}`,
      detail: 'Fix gate failures before deploy.',
    }
  } else {
    // Only S4-only regressions never trigger deploy (S1/S2/S3 heals do)
    const onlyS4 = actionableRegs.every(r => r.signal === 's4')
    if (onlyS4) {
      log('Deploy: all heals are S4-only — not deploying per contract.')
      deployResult = {
        attempted: false,
        deployed: false,
        dry: true,
        manifest: 'BLOCKED — only S4 advisory regressions present. S4-only never triggers deploy.',
        detail: 'S4 findings logged. No deploy.',
      }
    } else {
      deployResult = await agent(
        `You are the DEPLOY agent for the self-healing loop.

All gates are GREEN and autoDeploy is authorized.

Gate result:
${JSON.stringify(gateResult, null, 2)}

Files healed:
${healedSurfaces.join('\n')}

DEPLOY INSTRUCTIONS:
1. Verify env AUTO_DEPLOY=true exists (run: echo $AUTO_DEPLOY). If not set, set dry=true and abort.
2. Verify deploy settings permit STOPSHOW_ACK=1 bash ${DEPLOY_SH}.
3. Run: STOPSHOW_ACK=1 bash ${DEPLOY_SH}
4. After deploy, run post-verify: curl -s "https://skyyrose.co/?cb=$(date +%s)" and confirm HTTP 200 + size >= baseline.
5. Return deployed=true only if the script exits 0 AND post-verify passes.

SAFETY: NEVER self-grant permission. NEVER skip STOPSHOW_ACK check. If anything is uncertain, set dry=true and explain.

Return DEPLOY_SCHEMA.`,
        { schema: DEPLOY_SCHEMA, label: 'deploy', phase: 'Deploy' },
      )
      log(`Deploy: attempted=${deployResult.attempted}, deployed=${deployResult.deployed}, dry=${deployResult.dry}`)
    }
  }
}

// ================================================================
// PHASE 6 — LEARN-AFTER (runs every cycle — clean or not)
// ================================================================
phase('Learn-after')

const learnResult = await agent(
  `You are the LEARN-AFTER agent for the SkyyRose self-healing loop.

Your job: update the knowledge store, append the cycle log, and surface escalations.
This runs EVERY cycle — even clean cycles (to bump cycle count and track trends).

FILES TO UPDATE:
  Knowledge store : ${KNOWLEDGE}
  Heal log        : ${HEAL_LOG}
  Wolf memory     : ${WOLF_MEM}

CYCLE DATA:
  Cycle number      : ${diagnoseResult.cycle}
  Monitor timestamp : ${monitorResult.ts}
  Regressions       : ${JSON.stringify(regressions)}
  Escalations       : ${JSON.stringify(escalations)}
  Heal results      : ${JSON.stringify(healResults.map(r => ({ signature: r && r.reg && r.reg.signature, finalHealed: r && r.finalHealed, needsEscalate: r && r.needsEscalate, rootCauseFix: r && r.healAttempt && r.healAttempt.rootCauseFix, preventionAdded: r && r.healAttempt && r.healAttempt.preventionAdded })))}
  Gate              : ${JSON.stringify(gateResult)}
  Deploy            : ${JSON.stringify(deployResult)}

TASKS:

1. READ heal-knowledge.json. For each regression:
   a. If signature already exists in signatures[]: update it:
      - Increment recurrences by 1
      - Set lastSeen = this cycle's ts
      - Set lastOutcome = "healed" | "escalated" | "dry" | "gate-fail"
      - Append rootCauseFix and preventionAdded from the heal result
      - If healFailedConsecutive was tracked: increment if not healed, reset to 0 if healed
   b. If signature is new: append a new entry with all fields.
   c. For escalated signatures: set lastOutcome="escalated", increment healFailedConsecutive.
   Increment top-level "cycles" counter by 1.
   WRITE the updated knowledge store back to ${KNOWLEDGE}.

2. APPEND one JSON line to ${HEAL_LOG} (create file if it doesn't exist):
{
  "ts": "<monitor ts from this cycle>",
  "cycle": ${diagnoseResult.cycle},
  "signalsChecked": ["s1","s2","s3","s4"],
  "regressions": <array of regression signatures>,
  "healed": <array of signatures that finalHealed=true>,
  "improvements": <array of rootCauseFix strings>,
  "gate": <"green"|"red"|"skip">,
  "deployed": <true|false>,
  "dryManifest": <deploy manifest string or null>,
  "knowledgeUpdated": <array of signature strings upserted>,
  "lessons": <array of lesson strings learned this cycle>
}
(One line, no trailing newline, valid JSON.)

3. MINE step: identify any signature in the updated knowledge store with recurrences >= 3.
   For each, propose a structural fix AND a new monitor signal that would PREVENT it.
   Include in mineFindings[].

4. ESCALATIONS: for any signature that must be logged as unresolvable (healFailedConsecutive >= 2),
   append a one-line note to ${WOLF_MEM}:
   | <HH:MM> | ESCALATED: <signature> — failed heal >=2 consecutive cycles; founder review required | ${KNOWLEDGE} | escalated | ~50 |

5. NEW FAILURE CLASS: for any brand-new signature (not seen before):
   append a one-line note to ${WOLF_MEM}:
   | <HH:MM> | NEW regression class: <signature> (<description>) | ${KNOWLEDGE} | logged | ~50 |

Return LEARN_SCHEMA. Include real lessons learned, not generic placeholders.`,
  { schema: LEARN_SCHEMA, label: 'learn-after', phase: 'Learn-after' },
)

log(`Learn-after: cycle=${learnResult.cycle}, knowledgeUpdated=${(learnResult.knowledgeUpdated || []).length}, healLogAppended=${learnResult.healLogAppended}, mineFindings=${(learnResult.mineFindings || []).length}`)

// ================================================================
// RETURN
// ================================================================

return {
  loop:           'self-healing-theme-loop',
  cycle:          diagnoseResult.cycle,
  ts:             monitorResult.ts,
  clean:          diagnoseResult.clean,
  regressions:    regressions.length,
  escalations:    escalations.length,
  actionable:     actionableRegs.length,
  healed:         healResults.filter(r => r && r.finalHealed).length,
  gatePass:       gateResult ? gateResult.pass : null,
  deployed:       deployResult ? deployResult.deployed : false,
  dryManifest:    deployResult && deployResult.dry ? deployResult.manifest : null,
  knowledgeUpdated: learnResult.knowledgeUpdated || [],
  mineFindings:   learnResult.mineFindings || [],
  lessons:        learnResult.lessons || [],
  autoDeploy,
  monitor:        monitorResult,
  diagnose:       diagnoseResult,
  healResults,
  gate:           gateResult,
  deploy:         deployResult,
  learn:          learnResult,
}
