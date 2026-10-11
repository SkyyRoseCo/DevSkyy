# PRD: SkyyRose Asset ML Pipeline

## Overview

A unified machine learning pipeline for SkyyRose that automates product photo enhancement, learns brand DNA for consistent visual identity, generates AI-powered marketing visuals, creates SEO-optimized product copy, analyzes competitor trends, and enables 3D asset generation. The system uses Replicate as the ML backend and prioritizes **product authenticity** - the actual product is never AI-generated or altered, only enhanced and placed in AI-generated contexts.

**Core Principle:** Real products, enhanced presentation, AI-powered context and copy.

## Goals

- Automate product photo enhancement to reduce manual editing from hours to minutes
- Create industry-leading e-commerce visuals that convert while maintaining 100% product accuracy
- Learn and apply SkyyRose brand DNA (colors, lighting, composition, mood) consistently
- Generate AI lifestyle scenes, virtual try-ons, and marketing visuals around real products
- Auto-generate SEO-optimized product descriptions in SkyyRose's brand voice
- Analyze competitor visuals and industry trends to maintain competitive edge
- Enable 3D product visualization from 2D photography via Replicate models
- Support all image types: flat-lay, lifestyle, model photography, and UGC
- Integrate seamlessly with existing WooCommerce workflow with approval gates

## Quality Gates

These commands must pass for every user story:
```bash
pytest -v && isort . && ruff check --fix && black .
```

For API endpoints, also include:
- Manual API testing with curl/httpie examples in PR description
- Automated integration tests in `tests/integration/`

## Non-Functional Requirements

### Product Authenticity (CRITICAL)
- **NFR-1:** Pipeline MUST NOT alter product logos, branding, labels, or text
- **NFR-2:** Pipeline MUST NOT change product colors, textures, or physical features
- **NFR-3:** Pipeline MUST NOT add, remove, or modify product components
- **NFR-4:** All enhancements limited to: background, lighting, clarity, color accuracy, noise reduction
- **NFR-5:** Original unmodified image MUST be preserved alongside enhanced version
- **NFR-6:** AI-generated context imagery must use real product cutout, not AI-generated product

### AI Content Tracking
- **NFR-7:** All AI-generated imagery MUST contain invisible watermark for internal tracking
- **NFR-8:** Metadata MUST indicate AI-generation source and date

### Performance
- **NFR-9:** Standard enhancement processing < 30 seconds per image
- **NFR-10:** Batch processing support for 100+ images
- **NFR-11:** Queue-based async processing with status tracking

### Cost Efficiency
- **NFR-12:** Use Cloudflare R2 for storage (zero egress fees)
- **NFR-13:** Implement intelligent caching to avoid reprocessing
- **NFR-14:** Configurable quality tiers to balance cost/quality per task

---

## Phase 1: Photo Enhancement Pipeline

### US-001: Create Replicate client abstraction
**Description:** As a developer, I want a unified Replicate client so that all ML operations go through a consistent, testable interface.

**Acceptance Criteria:**
- [ ] Create `services/ml/replicate_client.py` with async client wrapper
- [ ] Support authentication via environment variable `REPLICATE_API_TOKEN`
- [ ] Implement retry logic with exponential backoff (max 3 retries)
- [ ] Add request/response logging with correlation_id
- [ ] Create `ReplicateError` exception class following project patterns
- [ ] Unit tests with mocked Replicate responses

### US-002: Implement image ingestion API endpoint
**Description:** As a user, I want to upload images via API so that external systems can submit images for processing.

**Acceptance Criteria:**
- [ ] Create `POST /api/v1/assets/ingest` endpoint
- [ ] Accept multipart/form-data with image file(s)
- [ ] Accept JSON metadata: `source`, `product_id`, `processing_profile`
- [ ] Validate image format (JPEG, PNG, WebP, TIFF)
- [ ] Validate image size (max 50MB, min 100x100px)
- [ ] Return job_id for async tracking
- [ ] Store original image to R2 with metadata
- [ ] Add to processing queue

### US-003: Implement WooCommerce auto-ingestion webhook
**Description:** As a store admin, I want new product images to automatically enter the pipeline so that I don't have to manually upload them.

**Acceptance Criteria:**
- [ ] Create webhook handler for WooCommerce product.created/updated events
- [ ] Extract product images from webhook payload
- [ ] Download and validate images
- [ ] Auto-submit to processing queue with `source: "woocommerce"`
- [ ] Link job to WooCommerce product_id for later sync
- [ ] Skip if image already processed (hash-based deduplication)

### US-004: Implement admin dashboard upload
**Description:** As a store admin, I want to manually upload images via dashboard so that I can process images not yet in WooCommerce.

**Acceptance Criteria:**
- [ ] Add upload component to existing admin dashboard
- [ ] Support drag-and-drop multiple files
- [ ] Show upload progress per file
- [ ] Allow selecting processing profile before upload
- [ ] Display job status after submission
- [ ] Link to job detail view

### US-005: Create background removal service
**Description:** As a user, I want product backgrounds removed/replaced so that images have clean, consistent backgrounds.

**Acceptance Criteria:**
- [ ] Integrate Replicate background removal model (recommend: `lucataco/remove-bg`)
- [ ] Preserve product edges with high precision (no halo artifacts)
- [ ] Support transparent PNG output
- [ ] Support solid color background replacement
- [ ] Support custom background image replacement
- [ ] **CRITICAL:** Verify product pixels unchanged via hash comparison of masked region
- [ ] Store both transparent and white-background versions

### US-006: Create lighting normalization service
**Description:** As a user, I want consistent lighting across all product images so that the catalog looks professional.

**Acceptance Criteria:**
- [ ] Integrate Replicate lighting/exposure model
- [ ] Normalize exposure without altering product colors
- [ ] Remove harsh shadows while maintaining depth
- [ ] Apply consistent soft lighting profile
- [ ] **CRITICAL:** Color calibration check - product colors must match original within Delta-E < 2
- [ ] Configurable intensity (subtle, moderate, strong)

### US-007: Create image upscaling service
**Description:** As a user, I want low-resolution images upscaled so that all images meet e-commerce quality standards.

**Acceptance Criteria:**
- [ ] Integrate Replicate upscaling model (recommend: `nightmareai/real-esrgan`)
- [ ] Support 2x and 4x upscaling
- [ ] Maintain sharpness without over-sharpening artifacts
- [ ] **CRITICAL:** Product text/logos must remain legible and unaltered
- [ ] Skip if image already meets minimum resolution (2000px longest edge)
- [ ] Output comparison metrics (PSNR, SSIM)

### US-008: Create format optimization service
**Description:** As a user, I want images automatically optimized for all platforms so that pages load fast and images look great everywhere.

**Acceptance Criteria:**
- [ ] Generate WebP for web (quality 85, < 500KB target)
- [ ] Generate optimized JPEG fallback (quality 90)
- [ ] Generate print-ready TIFF (300 DPI, uncompressed)
- [ ] Generate social variants: Instagram square (1080x1080), Pinterest (1000x1500)
- [ ] Generate thumbnail sizes: 150x150, 300x300, 600x600
- [ ] Preserve EXIF data for print files, strip for web
- [ ] Store all variants with consistent naming convention

### US-009: Create enhancement pipeline orchestrator
**Description:** As a user, I want a single pipeline that runs all enhancements in the correct order so that I get fully processed images with one request.

**Acceptance Criteria:**
- [ ] Create `services/ml/pipeline_orchestrator.py`
- [ ] Define pipeline stages: ingest → validate → background → lighting → upscale → format
- [ ] Support skipping stages via processing profile
- [ ] Run stages sequentially with intermediate storage
- [ ] Implement checkpoint/resume for failed jobs
- [ ] Emit events at each stage for monitoring
- [ ] Total pipeline < 2 minutes for standard image

### US-010: Create processing queue with fallback chain
**Description:** As a developer, I want failed ML tasks to automatically try alternative models so that processing continues despite model issues.

**Acceptance Criteria:**
- [ ] Implement job queue using existing infrastructure (or Redis if needed)
- [ ] Define fallback model chains per task type
- [ ] On primary model failure, automatically try fallback
- [ ] After all fallbacks exhausted, move to dead letter queue
- [ ] Admin notification on DLQ items
- [ ] Manual retry/skip interface for DLQ items
- [ ] Metrics: success rate, fallback rate, DLQ rate

### US-011: Create job status API
**Description:** As a user, I want to check processing status so that I know when my images are ready.

**Acceptance Criteria:**
- [ ] Create `GET /api/v1/assets/jobs/{job_id}` endpoint
- [ ] Return: status, current_stage, progress_percent, timestamps
- [ ] Return: output URLs when complete
- [ ] Return: error details if failed
- [ ] Create `GET /api/v1/assets/jobs` for listing user's jobs
- [ ] Support filtering by status, date range, source
- [ ] Webhook callback option for completion notification

### US-012: Implement product authenticity validator
**Description:** As a business owner, I want automated checks ensuring products aren't misrepresented so that we maintain customer trust and legal compliance.

**Acceptance Criteria:**
- [ ] Create `services/ml/authenticity_validator.py`
- [ ] Compare original vs enhanced using perceptual hashing on product region
- [ ] Flag if product region similarity < 95%
- [ ] Detect logo/text regions and verify unchanged
- [ ] Color accuracy check: Delta-E < 2 for product pixels
- [ ] Block auto-publish if validation fails
- [ ] Generate validation report with visual diff
- [ ] Human review queue for flagged images

---

## Phase 2: Brand DNA Learning

### US-013: Create brand asset ingestion for training
**Description:** As a brand manager, I want to feed our existing assets into the system so that it learns our visual identity.

**Acceptance Criteria:**
- [ ] Create bulk ingestion endpoint for training assets
- [ ] Accept categorized assets: products, lifestyle, campaigns, mood boards
- [ ] Extract and store: color palettes, composition patterns, lighting profiles
- [ ] Store metadata: campaign, season, photographer, approval status
- [ ] Minimum 500 assets for training baseline
- [ ] Progress tracking for large batch ingestion

### US-014: Generate brand DNA embeddings
**Description:** As a developer, I want brand assets converted to embeddings so that we can retrieve similar styles and maintain consistency.

**Acceptance Criteria:**
- [ ] Use Replicate CLIP or similar for image embeddings
- [ ] Store embeddings in existing vector store infrastructure
- [ ] Create embedding clusters: color, composition, mood, product-type
- [ ] Enable similarity search: "find images like this"
- [ ] Update embeddings when new approved assets added
- [ ] Expose via RAG query interface

### US-015: Create brand consistency scorer
**Description:** As a brand manager, I want to score how well new images match our brand so that off-brand content is flagged.

**Acceptance Criteria:**
- [ ] Compare new image embedding to brand cluster centroids
- [ ] Return brand_score (0-100) with breakdown by dimension
- [ ] Flag images scoring < 70 for review
- [ ] Provide suggestions: "lighting too harsh", "colors don't match palette"
- [ ] Track brand consistency over time (dashboard metric)

### US-016: Create style transfer service
**Description:** As a user, I want to apply SkyyRose brand style to images so that UGC and vendor photos match our aesthetic.

**Acceptance Criteria:**
- [ ] Integrate Replicate style transfer model
- [ ] Train/fine-tune on SkyyRose brand assets
- [ ] Apply brand lighting profile
- [ ] Apply brand color grading (without changing product colors)
- [ ] Configurable intensity (subtle, moderate, full)
- [ ] **CRITICAL:** Product authenticity validation before/after
- [ ] A/B comparison output for review

---

## Phase 3: 3D Asset Generation

### US-017: Refactor existing 3D services for Replicate
**Description:** As a developer, I want existing Tripo3D/FASHN services abstracted so that we can use Replicate models interchangeably.

**Acceptance Criteria:**
- [ ] Create `services/three_d/provider_interface.py` abstract base
- [ ] Implement `ReplicateProvider` using Replicate 3D models
- [ ] Maintain existing `Tripo3DProvider` and `FASHNProvider` as options
- [ ] Factory pattern for provider selection based on config
- [ ] Consistent input/output contract across providers
- [ ] Provider health checks and automatic failover

### US-018: Create 3D model generation from product photos
**Description:** As a user, I want to generate 3D models from product photos so that customers can view products from all angles.

**Acceptance Criteria:**
- [ ] Accept single image or multi-view images
- [ ] Generate GLB/GLTF 3D model via Replicate
- [ ] Support texture quality levels: preview, standard, high
- [ ] Processing time < 5 minutes for standard quality
- [ ] Store 3D asset with linked 2D source images
- [ ] Validate model has reasonable geometry (no major artifacts)

### US-019: Create 3D viewer embed component
**Description:** As a store admin, I want to embed 3D viewers on product pages so that customers can interact with products.

**Acceptance Criteria:**
- [ ] Create embeddable 3D viewer component (model-viewer or Three.js)
- [ ] Support GLB/GLTF loading from R2 CDN
- [ ] Touch/mouse rotation controls
- [ ] Zoom in/out
- [ ] Optional AR view (mobile)
- [ ] Lazy loading with placeholder image
- [ ] WordPress shortcode for easy embedding

### US-020: Create 3D thumbnail generator
**Description:** As a user, I want static renders from 3D models so that I can use them as additional product images.

**Acceptance Criteria:**
- [ ] Generate 4-8 angle renders from 3D model
- [ ] Consistent lighting matching brand profile
- [ ] Transparent background option
- [ ] Output at multiple resolutions
- [ ] Auto-add to product image gallery (with approval)

---

## Phase 4: Storage & Sync

### US-021: Implement Cloudflare R2 storage service
**Description:** As a developer, I want a storage abstraction using R2 so that we have cost-efficient, fast asset delivery.

**Acceptance Criteria:**
- [ ] Create `services/storage/r2_client.py`
- [ ] Implement: upload, download, delete, list, presigned URLs
- [ ] Organize by: `/originals/`, `/processed/`, `/3d/`, `/training/`, `/generated/`
- [ ] Set appropriate cache headers for CDN
- [ ] Implement lifecycle rules: delete temp files after 7 days
- [ ] Cost tracking and alerts

### US-022: Create WordPress media sync with approval
**Description:** As a store admin, I want processed images synced to WordPress after my approval so that only verified images go live.

**Acceptance Criteria:**
- [ ] Create approval queue UI in admin dashboard
- [ ] Show original vs processed side-by-side comparison
- [ ] Approve/reject with optional notes
- [ ] On approve: upload to WordPress media library via REST API
- [ ] On approve: update WooCommerce product gallery
- [ ] On reject: move to revision queue with feedback
- [ ] Batch approval for multiple images
- [ ] Email notification when images ready for review

### US-023: Create asset versioning system
**Description:** As a user, I want to access previous versions of processed images so that I can revert if needed.

**Acceptance Criteria:**
- [ ] Store all processing versions with timestamp
- [ ] Original always preserved (never deleted)
- [ ] Version history API endpoint
- [ ] Revert to previous version action
- [ ] Configurable retention: keep last N versions or last N days
- [ ] Storage cost impact visible in dashboard

---

## Phase 5: AI-Generated Product Imagery

### US-024: Create invisible watermarking service
**Description:** As a business owner, I want all AI-generated imagery to contain invisible watermarks so that we can track AI content internally.

**Acceptance Criteria:**
- [ ] Create `services/ml/watermark_service.py`
- [ ] Implement steganographic watermarking (invisible to human eye)
- [ ] Encode: generation date, model used, source product_id, job_id
- [ ] Watermark survives: compression, resizing, format conversion
- [ ] Create detection endpoint to extract watermark data
- [ ] Batch scanning tool for auditing existing assets
- [ ] Watermark not visible in any output format

### US-025: Create lifestyle scene generator
**Description:** As a marketer, I want to place real products in AI-generated lifestyle scenes so that we have aspirational marketing visuals without photoshoots.

**Acceptance Criteria:**
- [ ] Accept product image (with transparent background)
- [ ] Accept scene prompt: "luxury bedroom", "outdoor picnic", "modern office"
- [ ] Generate scene via Replicate (SDXL, Flux, or similar)
- [ ] Composite real product into generated scene with proper lighting/shadows
- [ ] **CRITICAL:** Product must be the actual cutout, not AI-regenerated
- [ ] Support scene style presets matching brand DNA
- [ ] Output multiple variations per prompt
- [ ] Apply invisible watermark to all outputs

### US-026: Create virtual try-on for apparel
**Description:** As a customer, I want to see how clothing looks on different body types so that I can make confident purchase decisions.

**Acceptance Criteria:**
- [ ] Integrate Replicate virtual try-on model (IDM-VTON, OOTDiffusion, or similar)
- [ ] Support model images: diverse body types, poses, skin tones
- [ ] Accept garment image and model image
- [ ] Generate realistic try-on with proper draping/fit
- [ ] **CRITICAL:** Garment colors, patterns, logos must match original exactly
- [ ] Support front and back views where applicable
- [ ] Generate 3-5 variations per garment
- [ ] Apply invisible watermark
- [ ] Output optimized for product pages and social

### US-027: Create marketing campaign visual generator
**Description:** As a marketer, I want to generate campaign visuals featuring our products so that we can rapidly create seasonal/promotional content.

**Acceptance Criteria:**
- [ ] Accept product images and campaign brief (theme, mood, text overlays)
- [ ] Generate hero images, banner variations, social posts
- [ ] Support aspect ratios: 16:9, 1:1, 9:16, 4:5
- [ ] Apply brand color palette and typography
- [ ] Support text overlay with brand fonts
- [ ] Generate 5-10 variations per campaign brief
- [ ] **CRITICAL:** Products must be real cutouts composited in
- [ ] Apply invisible watermark
- [ ] Export to design-ready formats (PSD layers if possible)

### US-028: Create AI imagery approval workflow
**Description:** As a brand manager, I want a dedicated review process for AI-generated imagery so that we maintain quality control.

**Acceptance Criteria:**
- [ ] Separate approval queue for AI-generated content
- [ ] Show: original product, generated output, prompt used, model info
- [ ] Quality checklist: product accuracy, brand alignment, professional quality
- [ ] Approve/reject/request revision workflow
- [ ] Revision requests include specific feedback
- [ ] Track approval rates by generation type
- [ ] Approved images auto-tagged with AI generation metadata

---

## Phase 6: Product Copywriting & Description Generation

### US-029: Create image-to-description pipeline
**Description:** As a store admin, I want product descriptions auto-generated from images so that I can rapidly populate product listings.

**Acceptance Criteria:**
- [ ] Accept product image(s) and category
- [ ] Extract visual features: color, material, style, details
- [ ] Generate base description (100-200 words)
- [ ] Use vision model via Replicate (LLaVA, BLIP, or similar)
- [ ] Support batch processing for catalog upload
- [ ] Return structured output: description, features list, suggested tags

### US-030: Create SEO-optimized description generator
**Description:** As a marketer, I want product descriptions optimized for search engines so that products rank well organically.

**Acceptance Criteria:**
- [ ] Accept base description and target keywords
- [ ] Generate SEO title (< 60 chars)
- [ ] Generate meta description (< 160 chars)
- [ ] Generate H1 and H2 suggestions
- [ ] Create bullet-point feature list (5-7 points)
- [ ] Generate long-form description (300-500 words)
- [ ] Include natural keyword placement
- [ ] Readability score (target: Grade 8 level)
- [ ] Output in structured JSON for easy WooCommerce import

### US-031: Create brand voice fine-tuning system
**Description:** As a brand manager, I want generated copy to match SkyyRose's voice so that all content feels authentically on-brand.

**Acceptance Criteria:**
- [ ] Ingest existing SkyyRose product descriptions (100+ examples)
- [ ] Extract brand voice characteristics: tone, vocabulary, sentence structure
- [ ] Create brand voice embedding/profile
- [ ] Apply voice transformation to generated descriptions
- [ ] A/B comparison: generic vs brand-voiced output
- [ ] Voice consistency scoring (compare to training examples)
- [ ] Support multiple voice variants: luxurious, playful, bold

### US-032: Create multi-language description generator
**Description:** As a global seller, I want descriptions in multiple languages so that we can expand to international markets.

**Acceptance Criteria:**
- [ ] Support languages: English, Spanish, French, German, Italian, Portuguese
- [ ] Generate from English source or directly from image
- [ ] Maintain brand voice across languages
- [ ] Cultural adaptation (not just translation)
- [ ] SEO optimization per language/market
- [ ] Native speaker quality validation checklist
- [ ] Store all language variants linked to product

### US-033: Create copy approval and editing workflow
**Description:** As a content manager, I want to review and refine generated copy before publishing so that quality is maintained.

**Acceptance Criteria:**
- [ ] Approval queue for generated descriptions
- [ ] Side-by-side: product image, generated copy, existing copy (if any)
- [ ] Inline editing with change tracking
- [ ] Approve/reject/request regeneration workflow
- [ ] Regenerate with feedback: "make it shorter", "more luxurious tone"
- [ ] Approved copy auto-syncs to WooCommerce
- [ ] Track edit rates to improve generation quality

---

## Phase 7: Competitor & Trend Analysis

### US-034: Create competitor image upload and tagging
**Description:** As a strategist, I want to upload and organize competitor imagery so that we can analyze their visual strategies.

**Acceptance Criteria:**
- [ ] Create competitor asset library (separate from brand assets)
- [ ] Upload interface with competitor name, product category, source URL
- [ ] Auto-extract visual features via ML
- [ ] Tag: composition type, color scheme, style, price positioning
- [ ] Store without processing (analysis only)
- [ ] GDPR-compliant: no scraping, manual upload only
- [ ] Access restricted to strategy/marketing roles

### US-035: Create visual style analyzer
**Description:** As a strategist, I want to analyze competitor visual styles so that we understand market positioning.

**Acceptance Criteria:**
- [ ] Generate embeddings for competitor images
- [ ] Cluster by visual style: minimal, luxurious, bold, lifestyle-heavy
- [ ] Compare SkyyRose style clusters to competitors
- [ ] Identify style gaps: "competitors use more lifestyle shots"
- [ ] Generate style comparison report
- [ ] Visualize brand positioning map (2D embedding projection)

### US-036: Create e-commerce trend analyzer
**Description:** As a strategist, I want to identify visual trends in fashion e-commerce so that we stay ahead of the market.

**Acceptance Criteria:**
- [ ] Accept trend research dataset (manually curated from industry sources)
- [ ] Identify emerging patterns: colors, compositions, presentation styles
- [ ] Track trend evolution over time
- [ ] Alert when new trends detected
- [ ] Generate "trend adoption" recommendations
- [ ] Monthly trend report generation
- [ ] Integration with brand DNA to suggest aligned trends

### US-037: Create competitive benchmarking dashboard
**Description:** As a manager, I want a dashboard comparing our visuals to competitors so that I can track our market position.

**Acceptance Criteria:**
- [ ] Dashboard showing: brand consistency score vs competitors
- [ ] Visual quality metrics comparison
- [ ] Style diversity analysis
- [ ] Trend adoption speed comparison
- [ ] Strengths/weaknesses summary
- [ ] Exportable report for stakeholders
- [ ] Refresh on new asset uploads

---

## Functional Requirements

- **FR-1:** System MUST preserve original images unmodified in cold storage
- **FR-2:** System MUST validate product authenticity before any auto-publish
- **FR-3:** System MUST support configurable processing profiles (speed vs quality)
- **FR-4:** System MUST provide job status via API and webhooks
- **FR-5:** System MUST retry failed ML tasks with fallback models
- **FR-6:** System MUST integrate with existing WooCommerce webhook system
- **FR-7:** System MUST use Replicate as primary ML backend
- **FR-8:** System MUST store all assets in Cloudflare R2
- **FR-9:** System MUST require human approval before WordPress sync
- **FR-10:** System MUST generate all output formats (web, print, social)
- **FR-11:** System MUST learn brand DNA from existing 500+ assets
- **FR-12:** System MUST score new images for brand consistency
- **FR-13:** System MUST support 3D model generation via Replicate
- **FR-14:** System MUST maintain audit trail with correlation_ids
- **FR-15:** System MUST apply invisible watermarks to all AI-generated imagery
- **FR-16:** System MUST generate SEO-optimized product descriptions
- **FR-17:** System MUST support multi-language description generation
- **FR-18:** System MUST apply brand voice to all generated copy
- **FR-19:** System MUST support competitor visual analysis without scraping
- **FR-20:** System MUST generate trend and benchmarking reports

## Non-Goals (Out of Scope)

- Real-time video processing (future consideration)
- Automated competitor website scraping (legal risk)
- Customer-facing chatbot integration
- Mobile app for photographers (API only)
- Custom ML model training from scratch (use pre-trained Replicate models)
- Multi-tenant/white-label support
- Social media auto-posting (generate assets only)
- Influencer content management

## Technical Considerations

- **Existing Infrastructure:** Leverage `services/three_d/` for 3D, `orchestration/vector_store.py` for embeddings
- **Replicate Models to Evaluate:**
  - Background removal: `lucataco/remove-bg`, `cjwbw/rembg`
  - Upscaling: `nightmareai/real-esrgan`, `tencentarc/gfpgan`
  - 3D generation: `adirik/wonder3d`, `camenduru/triposr`
  - Style transfer: `tencentarc/photomaker`, `lucataco/sdxl-lightning-4step`
  - Scene generation: `stability-ai/sdxl`, `black-forest-labs/flux-schnell`
  - Virtual try-on: `cuuupid/idm-vton`, `levihsu/ootdiffusion`
  - Vision/description: `yorickvp/llava-13b`, `salesforce/blip`
  - Text generation: Route through existing LLM infrastructure
- **Storage:** Cloudflare R2 with Workers for edge processing if needed
- **Queue:** Consider Redis + Bull for job queue, or leverage existing infrastructure
- **Monitoring:** Prometheus metrics for pipeline health, Replicate costs
- **Watermarking:** Consider `invisible-watermark` library or Replicate equivalent

## Success Metrics

| Metric | Target |
|--------|--------|
| Enhancement processing time | < 30 seconds standard |
| Product authenticity pass rate | > 99% |
| Brand consistency score (new images) | > 80 average |
| Manual editing time reduction | 80% reduction |
| Pipeline uptime | 99.5% |
| Cost per image processed | < $0.10 standard tier |
| WordPress sync approval rate | > 90% |
| AI imagery approval rate | > 75% first attempt |
| Generated copy approval rate | > 70% first attempt |
| Description edit rate | < 30% needing major edits |
| Multi-language quality score | > 85% native-equivalent |

## Open Questions

1. Should we implement watermarking for draft/unapproved images?
2. Do we need photographer attribution metadata preserved?
3. Should brand DNA model be shared with external vendors for pre-submission checking?
4. What's the budget ceiling for Replicate API costs per month?
5. Do we need GDPR considerations for any human subjects in lifestyle photos?
6. Should 3D models support AR Quick Look for iOS Safari?
7. For virtual try-on, do we need model release agreements for generated imagery?
8. Should generated descriptions support A/B testing integration?
9. What's the retention policy for competitor analysis data?
10. Do we need approval workflow for multi-language content per market?
