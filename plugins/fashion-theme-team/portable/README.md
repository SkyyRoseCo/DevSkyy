# Fashion Theme Team — global and portable installation

This is the same Fashion Theme Team knowledge and governance package across
hosts: 15 capability skills, 22 agent charters, bundled references, source
libraries and verification scripts. The Codex manifest remains intact.

## On this computer

Claude Code has a native plugin manifest. From the package root:

```bash
claude plugin marketplace add "$PWD" --scope user
claude plugin install fashion-theme-team@fashion-theme-team-local --scope user
```

Start a new Claude Code session and invoke
`/fashion-theme-team:fashion-theme-team`, followed by the task.
Claude automatically discovers the package's skills, agents and existing hooks.
Updates require `claude plugin update fashion-theme-team@fashion-theme-team-local`
and a new session. The Claude manifest version must change for a new release.

For Cursor, Gemini CLI and hosts that discover `~/.agents/skills`:

```bash
bash scripts/install-global.sh --apply
bash scripts/install-global.sh --check
```

This creates `fashion-theme-team-global` in `~/.cursor/skills`,
`~/.gemini/skills` and `~/.agents/skills`. It loads the complete package lazily
through a `package` symlink, so local source updates stay available. The installer
refuses unrelated existing destinations. Keep the source directory in place.
Restart Cursor; use `/skills reload` in Gemini CLI. Ask:

> Use fashion-theme-team-global to audit this storefront and carry the approved work through implementation and evidence.

On a different computer, extract the complete archive to a permanent directory
and run the same commands there. macOS/Linux Bash and symlinks are required by
the installer. Windows users can use WSL or manually copy the complete package
and adapt the router paths. Model selection remains the host's responsibility.

## ChatGPT, Claude web, Gemini web and other chat interfaces

Attach `PORTABLE-PROMPT.md` or paste it into project/custom instructions. It is a
standalone operating protocol. If the host can unpack and read archives, also
attach the complete archive; otherwise attach the selected skill, references and
charters needed for the task. This does not register native tools or autonomous
agents in a web chat. Full library access requires the corresponding files.
There is no universal plugin installation switch across LLM services.

## Compatibility and evidence

The shared instructions preserve exact product-source authority, spend and
publication approvals, separate builders and independent reviewers, and truthful
validation. Tool names are adapted to actual host capabilities. Missing tools or
independent review remain explicit gaps. Provider integrations and credentials
are configured separately; installing this package performs no generation.

Native Claude installation and component discovery can be checked with
`claude plugin details fashion-theme-team@fashion-theme-team-local`.
The global installer's check proves file/link availability, not an LLM session's
successful execution. Use an actual task in each host to assess behavior.

The full package verifier requires Python and `requirements-verify.txt`:

```bash
python3 -m venv /tmp/fashion-team-verify
/tmp/fashion-team-verify/bin/pip install -r requirements-verify.txt
PATH="/tmp/fashion-team-verify/bin:$PATH" bash scripts/verify.sh
```

Remove only the managed global routers with
`bash scripts/install-global.sh --remove`. Uninstall Claude separately with
`claude plugin uninstall fashion-theme-team@fashion-theme-team-local`.
The source and Codex installation remain available.

Official host references (checked 2026-09-07):
- https://code.claude.com/docs/en/plugins-reference
- https://geminicli.com/docs/cli/using-agent-skills/
- https://cursor.com/docs/skills

The package retains SkyyRose brand contracts and bundled third-party provenance;
it is usable with other LLM hosts but has not been relicensed or publicly published.
