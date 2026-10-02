# V2 typography and artwork provenance contract

This contract keeps page typography legally and semantically separate from
collection lockups. A font file may be used as a page font only when its
license, source, and byte hash are recorded; a SkyyRose graphic or custom
script remains approved artwork and is never presented as an open-source font.
The machine-readable evidence is
[`data/font-provenance.json`](../../../wordpress-theme/skyyrose-flagship-2/data/font-provenance.json).

## Page typography

Current page fonts (founder-approved "Stretch", 2026-10-02) are Anybody, Geist and
Martian Mono. Each is a Latin subset of the upstream variable font from
[google/fonts](https://github.com/google/fonts) @ `9710da1eacb3be272583c3224dcb70f9da6eadbb`;
the upstream commit, the google/fonts file and license hashes, and the exact
subset command are recorded per family in `data/font-provenance.json`. None of
the three declares a Reserved Font Name.

| Role | Family | Local file | Upstream (commit) | Delivery |
|---|---|---|---|---|
| Display | Anybody | `assets/sot/fonts/anybody-latin.woff2` | [Etcetera-Type-Co/Anybody](https://github.com/Etcetera-Type-Co/Anybody) (`fe7b55c`) | `derived/fonts/anybody-condensed.woff2` (wdth 50) and `anybody-wide.woff2` (wdth 150) |
| Body | Geist | `assets/sot/fonts/geist-latin.woff2` | [vercel/geist-font](https://github.com/vercel/geist-font) (`a6d260e`) | source file, weight axis 100–900 |
| Utility | Martian Mono | `assets/sot/fonts/martian-mono-latin.woff2` | [evilmartians/mono](https://github.com/evilmartians/mono) (`17865aa`) | `derived/fonts/martian-mono-narrow.woff2` (wdth 87.5) |

The width instances are built by `tools/v2-runtime/build-font-delivery.py`, which
fixes only the width axis and fails if coverage, metrics or name records change.

### Retired page fonts

The seven named upstream families below have copyright/source evidence in
their OpenType metadata and an upstream SIL OFL 1.1 record. The local
`OFL-1.1.txt` and `FONT-ATTRIBUTIONS.md` files satisfy the redistribution
notice bundle. A local font hash proves which bytes are in this candidate; it
does not prove an upstream commit, so `upstream_revision` remains an explicit
evidence field and must be filled before replacing any byte.

| Role | Family | Local file | Upstream provenance | License gate |
|---|---|---|---|---|
| Retired display | Archivo | `assets/sot/fonts/archivo-latin.woff2` | [Omnibus-Type/Archivo](https://github.com/Omnibus-Type/Archivo) | OFL 1.1; hash and revision in manifest; reserved-name notice in attribution file |
| Retired body | Hanken Grotesk | `assets/sot/fonts/hanken-grotesk-latin.woff2` | [marcologous/hanken-grotesk](https://github.com/marcologous/hanken-grotesk) | OFL 1.1; hash and revision in manifest; upstream attribution required |
| Retired utility | Anton | `assets/sot/fonts/anton-latin.woff2` | [googlefonts/AntonFont](https://github.com/googlefonts/AntonFont) | OFL 1.1; hash and revision in manifest; reserved-name notice in attribution file |
| Retired ceremonial metadata | Cinzel | `assets/sot/fonts/cinzel-latin.woff2` | [NDISCOVER/Cinzel](https://github.com/NDISCOVER/Cinzel) | OFL 1.1; preserve upstream attribution and reserved-name notice |
| Artifact candidate | Grand Hotel | `assets/sot/fonts/grand-hotel-latin.woff2` | Astigmatic / Grand Hotel | OFL 1.1; retained for artifact review, not registered as page type |
| Retired UI fallback | Inter | `assets/sot/fonts/inter-latin.woff2` | [rsms/inter](https://github.com/rsms/inter) | OFL 1.1; hash and revision in manifest; upstream attribution required |
| Artifact candidate | Pinyon Script | `assets/sot/fonts/pinyon-script-latin.woff2` | [SorkinType/Pinyon](https://github.com/SorkinType/Pinyon) | OFL 1.1; local metadata has no license URL, so retain attribution and revision gate |

The exact license text and copyright notice must ship with any redistributed
replacement bytes. The font files in the theme are a build projection; the
upstream project, license, and manifest hash are the authority, not the
filename.

### Evidence snapshot (2026-08-15)

`fontTools` inspection found upstream copyright and family metadata in all
seven known families. Pinyon Script has no local `nameID 14` license URL, but
its copyright metadata identifies the upstream project; the manifest keeps
that gap visible. The two `SkyyRose-*` files contain only a family/subfamily
name and no copyright, license, or upstream URL. They are not open-source
claims and remain blocked artwork.

The V1 authority (`wordpress-theme/skyyrose-flagship/data/brand/typography.json`
and its generated `assets/css/design-tokens.css`) separates universal roles
from a `collection_scripts` registry. V2 keeps the universal Archivo / Hanken
Grotesk / Anton / Cinzel / Inter roles, but does not carry V1's script names
into the page-font declarations; those names remain artifact metadata only.

## Collection artwork boundary

These files are not treated as open-source page typography:

- `skyyrose-black-rose-script-latin.woff2`
- `skyyrose-love-hurts-graffiti-latin.woff2`

Their internal family names identify them as SkyyRose artwork, but no license
or public upstream source is embedded in the files. They are therefore
reserved for founder-approved collection lockups, monument scenes, and other
art-directed artifacts. They must not be used for generic headings, exported
as a downloadable font, or substituted for the page type roles above until a
rights record exists.

## Collection mapping

| Collection | Page-type system | Approved artwork layer |
|---|---|---|
| Signature | Anybody / Geist / Martian Mono | Founder-approved Signature lockup or rose-gold graphic; Pinyon/Grand Hotel only when the source record says lockup artwork |
| Black Rose | Anybody / Geist / Martian Mono | Black Rose star graphic and founder-approved Black Rose script lockup |
| Love Hurts | Anybody / Geist / Martian Mono | Love Hurts star graphic and founder-approved graffiti lockup |
| Kids Capsule | Anybody / Geist / Martian Mono | Full-color heir/mascot and throne artwork; no monochrome statue substitute |
| Jersey Series (Black Rose release) | Anybody / Geist / Martian Mono | Jersey-specific marks and product imagery; retain the dedicated release treatment without inheriting core Black Rose artwork |

The CSS and `theme.json` mappings must continue to use the page-type system.
V2 `design-tokens.css` registers only Anybody Condensed, Anybody Wide, Geist and
Martian Mono; its legacy script slot aliases to the Martian Mono label face so an unproven face cannot
be pulled into generic headings. Collection-specific scripts and graphics
belong in image/artifact slots so they remain accessible, rights-reviewable,
and replaceable without changing the reading hierarchy.

## Verification gate

Before a font byte is changed, record its family, upstream commit/tag, license
file checksum, reserved-font-name obligations, and the candidate asset hash in
the SOT. Run `npm run verify` and the candidate media/rights gate. A missing
license, null upstream revision, unknown custom-face provenance, or unbound
lockup is `BLOCKED`, not an implicit approval. The presence of a local `.woff2`
or an OpenType family name is never proof of open-source rights.
