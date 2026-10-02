# V2 font attributions

The ten page-font files in this directory are redistributed under the SIL
Open Font License, Version 1.1. The complete license is in
[`OFL-1.1.txt`](./OFL-1.1.txt). The copyright notices below are required
attribution; they are not claims that the file bytes were rebuilt from a
known upstream revision.

| Family | Copyright / reserved-name notice | Upstream source | Local metadata evidence |
|---|---|---|---|
| Archivo | Copyright 2020 The Archivo Project Authors | [Omnibus-Type/Archivo](https://github.com/Omnibus-Type/Archivo) | name IDs 0, 14 |
| Hanken Grotesk | Copyright 2021 The Hanken Grotesk Project Authors | [marcologous/hanken-grotesk](https://github.com/marcologous/hanken-grotesk) | name IDs 0, 14 |
| Anton | Copyright 2020 The Anton Project Authors | [googlefonts/AntonFont](https://github.com/googlefonts/AntonFont) | name IDs 0, 14 |
| Cinzel | Copyright 2020 The Cinzel Project Authors; upstream also reserves “Cinzel Decorative” | [NDISCOVER/Cinzel](https://github.com/NDISCOVER/Cinzel) | name IDs 0, 14 |
| Grand Hotel | Copyright (c) 2012 Brian J. Bonislawsky DBA Astigmatic (AOETI); Reserved Font Name “Grand Hotel” | Astigmatic / Grand Hotel | name IDs 0, 14 |
| Inter | Copyright 2016 The Inter Project Authors | [rsms/inter](https://github.com/rsms/inter) | name IDs 0, 14 |
| Pinyon Script | Copyright 2022 The PinyonScript Project Authors | [SorkinType/Pinyon](https://github.com/SorkinType/Pinyon) | name ID 0; no local name ID 14 |
| Anybody | Copyright 2020 The Anybody Project Authors; no Reserved Font Name | [Etcetera-Type-Co/Anybody](https://github.com/Etcetera-Type-Co/Anybody) @ `fe7b55c`, via google/fonts @ `9710da1` | name IDs 0, 14 |
| Geist | Copyright 2024 The Geist Project Authors; no Reserved Font Name | [vercel/geist-font](https://github.com/vercel/geist-font) @ `a6d260e`, via google/fonts @ `9710da1` | name IDs 0, 14 |
| Martian Mono | Copyright 2021 The Martian Mono Project Authors (name ID 0 reads 2020); no Reserved Font Name | [evilmartians/mono](https://github.com/evilmartians/mono) @ `17865aa`, via google/fonts @ `9710da1` | name IDs 0, 14 |

The two `SkyyRose-*` files have no copyright, license, or public upstream
record in their OpenType metadata. They are therefore founder-controlled
artwork only and are intentionally absent from the page-font declarations.

Anybody, Geist and Martian Mono are the current page fonts (2026-10-02). They are
Latin subsets of the upstream variable fonts with every axis and name record
retained; the exact command and hashes are in `data/font-provenance.json`.
Archivo, Hanken Grotesk, Anton, Cinzel and Inter remain bundled for existing
artifact tooling but are no longer registered by the theme.
