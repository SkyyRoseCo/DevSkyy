Deploy the WordPress theme `wordpress-theme/skyyrose-flagship-2` ("SkyyRose Flagship 2") using the deploy-and-verify agent. The V1 theme `wordpress-theme/skyyrose-flagship` is not the deploy target.

Run the deploy-and-verify agent to:
1. Check PHP syntax (`npm run lint:php` in the theme folder) and `.min` drift (`npm run check:assets`)
2. Check for dead file references
3. Deploy — **BLOCKED until PR #918 lands: both wrappers refuse a `skyyrose-flagship-2` source, `--dry-run` included.** STOP-AND-SHOW, through the wrappers only, staging before production. One-shot flags `--allow-new-theme-folder` / `--allow-theme-identity-change` replace exporting `ALLOW_NEW_THEME_FOLDER` / `ALLOW_THEME_IDENTITY_CHANGE` (inherited exports are refused); the env file's `SSH_USER` must be `<first label of the PUBLIC_URL host>.wordpress.com` and `.env.wordpress.staging` needs `SFTP_HOST`/`SFTP_USER`/`SFTP_PASS`:
   `bash scripts/deploy-staging.sh [--dry-run]` (→ staging-7e48-skyyrose.wpcomstaging.com) then
   `bash scripts/deploy-production.sh [--dry-run]` (→ skyyrose.co; refuses until `.env.wordpress` `WP_THEME_PATH` names the `-2` folder). Never call `scripts/deploy-theme.sh` directly — it is the engine and refuses.
4. Flush server caches
5. Screenshot and verify every page in the agent's page list (cache-busted, mobile + desktop)

Report pass/fail for each page.
