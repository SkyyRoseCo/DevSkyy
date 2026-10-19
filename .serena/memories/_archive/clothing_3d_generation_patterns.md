# Clothing 3D Generation Patterns

**Purpose**: Filter product images to only generate 3D models for actual clothing items.

## Script Location

`scripts/generate_clothing_3d.py`

## Usage

```bash
# All collections
export TRIPO3D_API_KEY="tsk_..."
python3 scripts/generate_clothing_3d.py

# Specific collection
python3 scripts/generate_clothing_3d.py --collection black-rose

# Preview only (no generation)
python3 scripts/generate_clothing_3d.py --dry-run
```

## Clothing Keywords (INCLUDE)

These keywords in filenames indicate clothing items:

### Tops

- shirt, tee, t-shirt, tshirt, top, blouse, tank
- hoodie, hooded, sweatshirt, sweater, pullover, crewneck
- jacket, coat, blazer, cardigan, vest

### Bottoms

- pants, jeans, shorts, skirt, leggings, joggers, trousers

### Dresses

- dress, gown, romper, jumpsuit

### Outerwear

- sherpa, fleece, parka, windbreaker

### Accessories (Wearable)

- beanie, hat, cap, scarf, gloves

### Generic

- womens, women's, mens, men's, unisex

## Exclusion Patterns (SKIP)

These patterns indicate non-clothing items:

| Pattern | Description |
|---------|-------------|
| `logo` | Brand logos, not products |
| `skyyrosedad_*` | AI-generated rose artwork |
| `hyper-realistic.*rose` | Artistic rose images |
| `close-up.*rose` | Rose photography |
| `wide-angle.*rose` | Rose photography |
| `bleeding.*rose` | Artistic rose images |
| `glowing.*rose` | Artistic rose images |
| `IMG_*.HEIC` | iPhone raw photos (unknown content) |
| `[A-F0-9]{8}-[A-F0-9]{4}*` | UUID filenames (unknown content) |

## Adding New Patterns

To add new clothing keywords or exclusion patterns, edit:

- `scripts/generate_clothing_3d.py`
- Variables: `CLOTHING_KEYWORDS` and `EXCLUDE_PATTERNS`

## Output Structure

```
assets/3d-models-generated/
├── black-rose/
│   ├── BLACK Rose Sherpa.glb
│   ├── Womens Black Rose Hooded Dress.glb
│   └── ...
├── love-hurts/
│   └── ...
├── signature/
│   └── ...
└── CLOTHING_GENERATION_SUMMARY.json
```

## API Response Structure (Important!)

The Tripo3D API returns models at `output.pbr_model`, NOT `output.model`.

```python
# Correct way to get model URL
model_url = response["data"]["output"]["pbr_model"]
```

## Troubleshooting

- **Timeout issues**: Each model takes ~60-90 seconds. Ensure polling timeout is at least 5 minutes.
- **SSL errors**: Use `ssl.CERT_NONE` context or install certifi
- **Balance check**: `GET /v2/openapi/user/balance`

## Cost Estimation

- ~30 credits per 3D model
- Check balance: Shown at script start
- Current balance endpoint: `https://api.tripo3d.ai/v2/openapi/user/balance`
