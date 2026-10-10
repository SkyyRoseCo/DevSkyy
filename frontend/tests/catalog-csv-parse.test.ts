import { readFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { parseCsvRecords } from '@/lib/catalog-csv';

// The catalog projection is generated from the product registry and carries
// multi-line garment specifications. A parser that splits lines first turns
// every continuation line into a fake product (70 of them, 2026-09-18).
const replica = path.resolve(import.meta.dirname, '../data/skyyrose-catalog.csv');
const registry = path.resolve(
  import.meta.dirname,
  '../../wordpress-theme/skyyrose-flagship/data/logo-registry.json'
);

describe('parseCsvRecords', () => {
  it('keeps a quoted newline inside its cell', () => {
    expect(parseCsvRecords('sku,fit\nbr-001,"relaxed\nthrough the body"\n')).toEqual([
      ['sku', 'fit'],
      ['br-001', 'relaxed\nthrough the body'],
    ]);
  });

  it('handles escaped quotes, CRLF, and blank lines', () => {
    expect(parseCsvRecords('a,b\r\n"say ""hi""",2\r\n\r\nx,\n')).toEqual([
      ['a', 'b'],
      ['say "hi"', '2'],
      ['x', ''],
    ]);
  });

  it('fails closed on an unterminated quote', () => {
    expect(() => parseCsvRecords('a,b\n"open,1\n')).toThrow(/unterminated/);
  });

  it('reads the deployment replica as exactly the registry products', () => {
    const records = parseCsvRecords(readFileSync(replica, 'utf8'));
    const [headers, ...rows] = records;
    const skuAt = headers.indexOf('sku');
    const skus = rows.map((cells) => cells[skuAt]);
    const expected = Object.keys(JSON.parse(readFileSync(registry, 'utf8')).products);
    expect(rows.every((cells) => cells.length === headers.length)).toBe(true);
    expect(skus.sort()).toEqual(expected.sort());
  });
});
