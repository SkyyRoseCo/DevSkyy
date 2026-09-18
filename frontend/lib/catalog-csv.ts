/**
 * Pure CSV transforms for the SkyyRose catalog projection.
 *
 * This module is intentionally DEPENDENCY-FREE: no `node:fs`, no `server-only`,
 * no `@/` aliases. That keeps it unit-testable in isolation and reusable from
 * both the read path (`catalog.ts`) and the write path (`catalog-write.ts`).
 *
 * The catalog CSV is a GENERATED projection of the product registry
 * (`logo-registry.json`). This module only READS that projection; writes go
 * through the registry writer (`catalog-write.ts` → Python
 * `update_catalog_fields`), which regenerates the CSV. Nothing here serializes
 * or splices CSV rows.
 */

/** Columns an editor is allowed to write. Everything else (sku, collection,
 *  garment_type_lock, dossier_slug, and the SOT-governed image columns) is
 *  read-only. Mirrors the allow-list enforced by `update_catalog_fields`. */
export const EDITABLE_COLUMNS = [
  'name',
  'price',
  'badge',
  'sizes',
  'color',
  'edition_size',
  'published',
  'is_preorder',
  'description',
] as const;

export type EditableColumn = (typeof EDITABLE_COLUMNS)[number];

/** A patch maps editable column names to their raw catalog cell string. */
export type CatalogPatch = Partial<Record<EditableColumn, string>>;

/**
 * Parse CSV text into records (RFC 4180): quoted cells may contain commas,
 * escaped quotes (`""`), and newlines. The registry's catalog projection carries
 * multi-line garment specifications (fit, materials, features), so a line split
 * before parsing would turn each continuation line into a bogus product row.
 * Blank lines between records are skipped.
 */
export function parseCsvRecords(text: string): string[][] {
  const records: string[][] = [];
  let record: string[] = [];
  let cell = '';
  let inQuotes = false;
  const endRecord = () => {
    record.push(cell);
    if (record.length > 1 || record[0] !== '') records.push(record);
    record = [];
    cell = '';
  };
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"' && text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cell += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      record.push(cell);
      cell = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i += 1;
      endRecord();
    } else {
      cell += ch;
    }
  }
  if (inQuotes) throw new Error('Malformed CSV: unterminated quoted cell');
  if (cell !== '' || record.length > 0) endRecord();
  return records;
}

/**
 * Collapse CR/LF runs to a single space. The editable catalog fields (name,
 * badge, sizes, color, description) are single-line values; the API layer
 * normalizes free text through this before handing it to the registry writer.
 */
export function collapseNewlines(value: string): string {
  return value.replace(/\r\n|\r|\n/g, ' ');
}
