# Dependency + Environment Audit

## Node dependency pinning

Top-level packages now use exact versions for the drifted entries found by
`npm ls`:

- `graphql@17.0.2`
- `jest@30.4.2`
- `jest-environment-jsdom@30.4.1`
- `lucide-react@1.28.0`
- `pica@10.0.2`
- `rate-limiter-flexible@11.2.0`
- `sharp@0.35.4` — security patch for GHSA-rgj7-g3m4-5g8c (2026-09-14)
- `three@0.185.1`
- `ts-jest@29.4.12`
- `vite@8.2.0`
- `webpack-cli@7.2.2`

## WordPress environment split

Keep `.env.wordpress` focused on WordPress transport and deploy access:

- `WORDPRESS_SITE_URL`
- `WORDPRESS_API_TOKEN`
- `WOOCOMMERCE_KEY`
- `WOOCOMMERCE_SECRET`
- `WC_WEBHOOK_SECRET`
- `SSH_*`, `SFTP_*`, `WP_CLI_SSH`, `WP_THEME_PATH`

Keep app/runtime secrets in `.env`:

- `DATABASE_URL`, `REDIS_URL`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY`
- `STRIPE_*`, `SMTP_*`, `KLAVIYO_*`
- `WORDPRESS_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`

## Notes

- `npm audit` still reports many advisories in transitive packages.
- `composer audit` still reports advisories in `composer/composer` and
  `wp-coding-standards/wpcs`.
- Do not commit real secret values; only align example files and documentation.
