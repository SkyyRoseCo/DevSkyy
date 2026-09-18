import path from 'node:path';
import * as prettier from 'prettier';
import { describe, expect, it } from 'vitest';

// The product registry and its dossier projections are byte-compared by
// `sync_product_registry.py --check`, and the registry is sha256-pinned in the
// asset manifest. Prettier must leave them alone in every entry point that reads
// .prettierignore -- editors and CI checks, not only the pre-commit hook
// (that path is covered in lint-staged-merge.test.ts).
const root = path.resolve(import.meta.dirname, '../../..');
const ignorePath = path.join(root, '.prettierignore');

const ignored = async (relative: string) =>
  (await prettier.getFileInfo(path.join(root, relative), { ignorePath })).ignored;

describe('prettier leaves the product SOT byte-stable', () => {
  it.each([
    'wordpress-theme/skyyrose-flagship/data/logo-registry.json',
    'wordpress-theme/skyyrose-flagship/data/dossiers/black-rose-crewneck.md',
    'logo-registry.json',
  ])('ignores %s', async relative => {
    expect(await ignored(relative)).toBe(true);
  });

  it('still formats ordinary Markdown beside the dossiers', async () => {
    expect(await ignored('wordpress-theme/skyyrose-flagship/data/brand-logos/sr-monogram.md')).toBe(false);
  });
});
