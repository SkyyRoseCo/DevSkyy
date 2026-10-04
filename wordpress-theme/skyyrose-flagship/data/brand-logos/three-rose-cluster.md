---
logo_id: black-roses-cloud-cluster
collection: shared
image_path: data/brand-logos/three-rose-cluster.jpeg
aliases:
  - three-rose-cluster
  - black-rose
---

# Three-Rose Cluster — Canonical Shared Art

This is the SINGLE source of truth for the three-rose-cluster art. It is used
across multiple collections — it is the Black Rose collection's primary logo,
and it also appears (recolored) on select Signature pieces. Any dossier that
says "the three-rose-cluster" or "the Black Rose logo" references this file.
Update here and the change propagates to every product.

## Visual Description

A vertical cluster of three illustrated roses on a cloud, with thorny green
vines wrapping around the stems:

- **Three roses, vertically stacked, illustrated comic-book style** with hard
  ink edges and soft tonal shading on the petals.
  - One **large rose bloom** dominant in the upper portion of the composition,
    fully open, viewed face-on.
  - One **medium bloom** on the upper-left, three-quarter angle, slightly smaller.
  - One **smaller bud or partially-open rose** lower in the cluster.
  - A few **leaves** behind / between the blooms.
- **Petals are greyscale** in the base art — light grey at the highlights, dark
  grey to near-black at the shadows, with bold ink outlines. NOT photo-realistic.
  NOT solid black. NOT solid white.
- **Stems are bright kelly green** — saturated, slightly cartoony, with darker
  green shading on the underside of each stem.
- **Thorny vines** wrap around the stems and twist between the blooms. Thorns
  are clearly visible — short, sharp, dark-green spikes along the stems.
- **A small white-and-light-blue cumulus cloud** sits at the very base of the
  cluster, like a pedestal under the stems. The cloud has soft pillowy lobes
  and subtle pale-blue shading on the underside.
- The composition is **roughly oval/teardrop overall** — wider near the top
  (the rose blooms), narrower at the bottom (where stems meet the cloud),
  bottom anchored by the cloud.

## Per-collection / per-SKU colorways

The art SHAPES stay constant; the colorway is recolored per product (the dossier
specifies the recolor):

- **Black Rose** — greyscale/embossed base palette (BLACK blooms, WHITE cloud,
  GREY stems/vines on the embossed colorway; full kelly-green palette on
  silicone appliqué / screen-print).
- **Signature 'Stay Golden' Shirt (sg-002)** — recolored to **purple**.
- **Signature 'Bay Bridge' Shirt (sg-005)** — recolored to **blue/cyan**.
- **Signature Beanie (sg-007)** — resolve the selected variant from its actual product artwork. The registry records an open variant/technique conflict; do not use greyscale as a universal default.
- **Mint & Lavender (sg-006 hoodie, sg-013 crewneck, sg-014 sweatpants)** — small **lavender**
  rose-cluster recolor (founder-confirmed 2026-06-11 from the techflat; the
  earlier 'pink' note was stale — the real garment shows lavender/purple roses).


Colorway-correct render references (selective recolor of this base art, used
as attached references so the image model copies the right rose color) live
at `assets/products/logos/three-rose-cluster-{greyscale,lavender,pink,purple,
blue-cyan}.png` and are wired per SKU in `scripts/oai_render/references.py`.

## What this logo IS NOT

- NOT a single rose silhouette.
- NOT a solid-black tonal mark.
- NOT a "B" or "BR" monogram (those are different logos in the brand system).
- NOT the abstract photographic black-rose-with-gold-accents at
  `assets/branding/black-rose-logo.png` (that file is a hero treatment for
  collection landing pages, not the product brandable logo).

## How techniques apply this art

Different products apply this art via different techniques. The art stays the
same; the texture/colorway changes per technique:

- **Embossed** (e.g., Black Rose Crewneck): raised dimensional relief on the
  fabric surface — visibly 3D and tactile, NOT debossed/sunken, NOT a flat
  print. Embossed colorway is a reduced 3-color palette: **BLACK** (rose
  blooms), **WHITE** (cumulus cloud at base), **GREY** (stems, leaves, thorny
  vines). NO kelly-green stems and NO blue cloud shading on the embossed
  version — those canonical colors only appear in techniques that preserve the
  full palette. The full canonical art SHAPES are preserved (three roses +
  leaves + stems + thorny vines + cumulus cloud); only the colorway is reduced.
- **Silicone appliqué** (e.g., Black Rose Joggers): raised silicone patch with
  full multi-color art preserved.
- **Embroidered**: thread version of the art. Colors approximated in thread.
- **Embroidered patch**: same as embroidered, stitched onto a fabric backing
  patch sewn onto the garment.
- **Printed / DTG / screen-print**: flat-ink full-color version.
- **Tackle twill**: felt/twill cut-shape appliqué.

## Reference Image

Image file: `data/brand-logos/three-rose-cluster.jpeg`. Pipelines that build
RAS prompts attach this image as a reference (after the 3D scaffold and the
techflat) when rendering any product whose dossier names this art.
