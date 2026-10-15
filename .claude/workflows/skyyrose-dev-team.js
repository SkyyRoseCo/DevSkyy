export const meta = {
  name: 'skyyrose-dev-team',
  description:
    'Commercial-grade SkyyRose dev team. Plan -> batched frontend/backend build -> per-checkpoint code-review-fix loop -> WordPress health sweep -> synthesize. Every agent reads the team charter first and works at the /efficient-production bar, never generic. Auto-recommended on WordPress/dashboard work.',
  phases: [
    { title: 'Plan', detail: 'Lead architect grounds in real code and decomposes into FE/BE workstreams with pinned files' },
    { title: 'Build', detail: 'Batched frontend/backend engineers build at the /efficient-production bar' },
    { title: 'Review', detail: 'code-review --fix loop after every checkpoint until CRITICAL/HIGH clear' },
    { title: 'WP Health', detail: 'Static WordPress sweep: duplicate pages, broken code, templates, PHPCS, security, assets' },
    { title: 'Synthesize', detail: 'Report changed files, verify status, and what the founder should eyeball' },
  ],
}

const REPO = '/Users/theceo/DevSkyy'
const CHARTER = '/Users/theceo/DevSkyy/.claude/workflows/skyyrose-dev-team-context.html'
const READ_FIRST =
  `BEFORE anything else, Read ${CHARTER} in full and obey it. It is the team charter: SkyyRose brand canon, ` +
  `the /efficient-production standard, anti-generic driven examples (good vs bad), the role->skill map, and hard rules. ` +
  `Generic output is a failure, not a draft.`

// ---------------------------------------------------------------- schemas

const PLAN_SCHEMA = {
  type: 'object',
  required: ['surface', 'summary', 'workstreams', 'touchesWp', 'touchesApi'],
  properties: {
    surface: { type: 'string', enum: ['wp', 'dashboard', 'api', 'mixed'] },
    summary: { type: 'string' },
    touchesWp: { type: 'boolean' },
    touchesApi: { type: 'boolean' },
    workstreams: {
      type: 'array',
      items: {
        type: 'object',
        required: ['batch', 'title', 'detail', 'files'],
        properties: {
          batch: { type: 'string', enum: ['frontend', 'backend', 'marketing'] },
          title: { type: 'string' },
          detail: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          acceptance: { type: 'string' },
        },
      },
    },
  },
}

const BUILD_SCHEMA = {
  type: 'object',
  required: ['status', 'filesChanged', 'summary'],
  properties: {
    status: { type: 'string', enum: ['done', 'partial', 'blocked'] },
    filesChanged: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
    followups: { type: 'array', items: { type: 'string' } },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['clean', 'fixesApplied', 'remaining', 'verifyOutput'],
  properties: {
    clean: { type: 'boolean' },
    fixesApplied: { type: 'array', items: { type: 'string' } },
    verifyOutput: { type: 'string' },
    remaining: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'issue'],
        properties: {
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          file: { type: 'string' },
          issue: { type: 'string' },
        },
      },
    },
  },
}

const HEALTH_SCHEMA = {
  type: 'object',
  required: ['pass', 'checks', 'criticalFindings'],
  properties: {
    pass: { type: 'boolean' },
    criticalFindings: { type: 'array', items: { type: 'string' } },
    checks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'status'],
        properties: {
          name: { type: 'string' },
          status: { type: 'string', enum: ['pass', 'warn', 'fail'] },
          detail: { type: 'string' },
        },
      },
    },
  },
}

const SYNTH_SCHEMA = {
  type: 'object',
  required: ['changedFiles', 'verifyStatus', 'report', 'eyeball'],
  properties: {
    changedFiles: { type: 'array', items: { type: 'string' } },
    verifyStatus: { type: 'string' },
    report: { type: 'string' },
    eyeball: { type: 'array', items: { type: 'string' } },
  },
}

// ---------------------------------------------------------------- helpers

function normalizeTask(a) {
  if (!a) return { task: '', surface: 'auto', scope: [] }
  if (typeof a === 'string') return { task: a, surface: 'auto', scope: [] }
  return { task: a.task || a.prompt || '', surface: a.surface || 'auto', scope: a.scope || [] }
}

function agentFor(batch) {
  if (batch === 'marketing') return 'skyyrose-launch-commander'
  return batch === 'frontend' ? 'frontend-developer' : 'Backend Architect'
}

function fileList(files) {
  return files && files.length ? files.join(', ') : '(not pinned by plan — read to locate, stay minimal)'
}

// ---------------------------------------------------------------- run

const input = normalizeTask(args)
if (!input.task) {
  log('skyyrose-dev-team: no task provided. Invoke with args = "<what to build or fix>".')
  return { error: 'no-task' }
}

// PHASE 1 — PLAN
phase('Plan')
const plan = await agent(
  `${READ_FIRST}\n\nYou are the LEAD ARCHITECT. Task from the founder:\n"""${input.task}"""\n` +
    `Surface hint: ${input.surface}. Scope hint: ${fileList(input.scope)}.\n\n` +
    `Read the relevant code in ${REPO} to ground EVERY decision (never guess paths). Then decompose into a tight build plan:\n` +
    `- surface: wp | dashboard | api | mixed.\n` +
    `- workstreams: each tagged batch=frontend or backend, with title, concrete detail, the EXACT files it will create/edit, and an acceptance criterion. PARTITION files so no two workstreams touch the same file (lets them build in parallel safely). If two pieces must share a file, merge them into one workstream.\n` +
    `- Frontend = WP templates/CSS/JS + Next.js UI. Backend = WP PHP/WooCommerce + Next server/API + FastAPI Python API.\n` +
    `- touchesWp / touchesApi booleans.\n` +
    `No speculative work. Only what the task needs.`,
  { agentType: 'architect', schema: PLAN_SCHEMA, label: 'plan', phase: 'Plan' },
)

const workstreams = (plan.workstreams || []).filter(Boolean)
if (!workstreams.length) {
  log('Planner produced no workstreams — nothing to build.')
  return { plan, built: [], error: 'empty-plan' }
}
log(`Plan ready: ${workstreams.length} workstream(s), surface=${plan.surface}.`)

// PHASE 2 + 3 — BUILD, then REVIEW-FIX loop, pipelined per workstream
const deepBudget = !!(budget && budget.total && budget.remaining() > 400000)
const REVIEW_CAP = deepBudget ? 3 : 2

const results = await pipeline(
  workstreams,
  // stage 1 — build
  (ws, _orig, i) =>
    agent(
      `${READ_FIRST}\n\nYou are a ${String(ws.batch).toUpperCase()} engineer. Build this checkpoint:\n` +
        `Title: ${ws.title}\nDetail: ${ws.detail}\n` +
        `Files you OWN (edit ONLY these): ${fileList(ws.files)}\n` +
        `Acceptance: ${ws.acceptance || 'meets the task and the charter bar'}\n\n` +
        `Invoke the skills the charter maps to your surface. Read each file before editing; match existing patterns. ` +
        `Production-ready only — no TODO/placeholder/mock. Do NOT run repo-wide formatters or linters (that is the review stage). Return exactly what you changed.`,
      { agentType: agentFor(ws.batch), schema: BUILD_SCHEMA, label: `build:${ws.batch}:${i}`, phase: 'Build' },
    ),
  // stage 2 — code-review --fix loop (runs as soon as each build completes)
  async (build, ws, i) => {
    if (!build || build.status === 'blocked') {
      return { ws: ws.title, batch: ws.batch, build, review: null, blocked: true, clean: false }
    }
    let review = null
    for (let attempt = 1; attempt <= REVIEW_CAP; attempt++) {
      review = await agent(
        `${READ_FIRST}\n\nRun /code-review --fix on this checkpoint (attempt ${attempt}/${REVIEW_CAP}).\n` +
          `Checkpoint: ${ws.title}\n` +
          `Files: ${fileList(build.filesChanged && build.filesChanged.length ? build.filesChanged : ws.files)}\n\n` +
          `Follow section 6 of the charter: review the diff at the /efficient-production bar (correctness -> security -> brand canon -> reuse). ` +
          `APPLY fixes for every CRITICAL and HIGH inline. Re-verify by RUNNING the real check (php -l on touched PHP via /opt/homebrew/bin/php; npm run type-check for dashboard; pytest -x for Python) and put the real output in verifyOutput. ` +
          `Return clean=true ONLY when no CRITICAL/HIGH remain. Make real progress each pass.`,
        { agentType: 'code-reviewer', schema: REVIEW_SCHEMA, label: `review:${ws.batch}:${i}:a${attempt}`, phase: 'Review' },
      )
      if (!review || review.clean) break
    }
    return { ws: ws.title, batch: ws.batch, build, review, clean: !!(review && review.clean), blocked: false }
  },
)

const built = results.filter(Boolean)

// PHASE 4 — WORDPRESS HEALTH SWEEP (static; only when WP is touched)
phase('WP Health')
let health = null
const wpTouched = plan.surface === 'wp' || plan.surface === 'mixed' || plan.touchesWp === true
if (wpTouched) {
  health = await agent(
    `${READ_FIRST}\n\nRun the WordPress health-check sweep (section 7 of the charter) over the changes just made in ` +
      `${REPO}/wordpress-theme/skyyrose-flagship-2 (V2 "SkyyRose Flagship 2", text domain skyyrose-flagship-2, ` +
      `SKYYROSE2_VERSION, own package.json — the lineage skyyrose.co and staging serve) — or ` +
      `${REPO}/wordpress-theme/skyyrose-flagship (V1 "SkyyRose", text domain skyyrose, SKYYROSE_VERSION, ` +
      `builds via wordpress-theme/package.json) if that is the theme the plan edited. State which theme in the report.\n` +
      `STATIC ONLY — do NOT deploy or curl production.\n` +
      `Check all 7 items: (1) duplicate pages (theme-activation-setup slug collisions + SETUP_VERSION gate), ` +
      `(2) broken code (php -l via /opt/homebrew/bin/php on touched PHP), ` +
      `(3) templates not rendering (enqueue.php slug map matches template filenames; get_template_part targets exist; front-page manual includes), ` +
      `(4) PHPCS (phpcs -s on touched files with THAT theme's ruleset — skyyrose-flagship/.phpcs.xml, skyyrose-flagship-2/phpcs.xml; the binary is skyyrose-flagship/vendor/bin/phpcs, skyyrose-flagship-2 has no vendor/), ` +
      `(5) security (no innerHTML; escaping; sanitize; nonce+capability; no hardcoded secrets), ` +
      `(6) assets exist + that theme's version constant (SKYYROSE2_VERSION for skyyrose-flagship-2, SKYYROSE_VERSION for skyyrose-flagship) bumped when CSS/JS changed, ` +
      `(7) no regression / no resurrection of retired patterns.\n` +
      `Report each check pass/warn/fail with file:line evidence. If a CRITICAL item fails, APPLY the fix and re-check. Return pass=true only when the sweep is green.`,
    { agentType: 'wp-code-simplifier', schema: HEALTH_SCHEMA, label: 'wp-health', phase: 'WP Health' },
  )
} else {
  log('No WordPress surface touched — skipping WP health sweep.')
}

// PHASE 5 — SYNTHESIZE
phase('Synthesize')
const blockedNames = built.filter((b) => b.blocked).map((b) => b.ws)
const synth = await agent(
  `You are the delivery lead reporting a team run to the founder (Corey). Be terse and concrete.\n` +
    `Run \`git -C ${REPO} status --porcelain\` and \`git -C ${REPO} diff --stat\` to list the files that ACTUALLY changed.\n` +
    `Run summary: ${built.length} checkpoint(s) built; review-clean ${built.filter((b) => b.clean).length}/${built.length}; ` +
    `blocked: ${blockedNames.length ? blockedNames.join('; ') : 'none'}; ` +
    `WP health: ${health ? (health.pass ? 'green' : 'has findings — see criticalFindings') : 'n/a'}.\n` +
    `Produce: changedFiles (from git), verifyStatus (one line on what was actually run and passed — quote nothing you did not run), ` +
    `report (tight, per-checkpoint, what shipped), and eyeball (specific things the founder should visually check). No fluff, no praise.`,
  { schema: SYNTH_SCHEMA, label: 'synthesize', phase: 'Synthesize' },
)

return {
  surface: plan.surface,
  planSummary: plan.summary,
  workstreams: workstreams.length,
  built,
  health,
  synthesis: synth,
}
