# Dependencies Reference

**Version**: 3.2.0
**Last Updated**: 2026-02-22

Complete reference for all Python and JavaScript/TypeScript dependencies used in the DevSkyy platform.

---

## Python Dependencies

**Source**: `pyproject.toml`
**Total**: 46 core dependencies + optional dependency groups

### Core Framework

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.104 | Web framework for APIs |
| `uvicorn[standard]` | >=0.24 | ASGI server |
| `mangum` | >=0.18.0 | ASGI adapter for serverless |
| `pydantic` | >=2.5 | Data validation |
| `pydantic-settings` | >=2.1 | Settings management |
| `python-multipart` | >=0.0.22 | File uploads |

### Database

| Package | Version | Purpose |
|---------|---------|---------|
| `sqlalchemy` | >=2.0 | ORM |
| `alembic` | >=1.13 | Migrations |
| `asyncpg` | >=0.29 | PostgreSQL async driver |
| `aiosqlite` | >=0.19 | SQLite async driver |

### Security

| Package | Version | Purpose |
|---------|---------|---------|
| `PyJWT` | >=2.8 | JWT tokens |
| `passlib[bcrypt]` | >=1.7 | Password hashing |
| `argon2-cffi` | >=23.1 | Argon2 hashing |
| `cryptography` | >=41 | Encryption |
| `bcrypt` | >=4.1 | Bcrypt hashing |

### HTTP

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | >=0.25 | Async HTTP client |
| `aiohttp` | >=3.9 | Async HTTP |
| `requests` | >=2.31 | Sync HTTP client |

### AI/ML & MCP

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.6 | OpenAI API |
| `mcp` | >=1.23.0 | Model Context Protocol |
| `anthropic` | >=0.75.0 | Claude API |
| `google-genai` | >=1.50.0 | Gemini API |
| `cohere` | >=5.20.0 | Cohere API |
| `mistralai` | >=1.10.1 | Mistral API |
| `groq` | >=0.37.0 | Groq API |

### Monitoring

| Package | Version | Purpose |
|---------|---------|---------|
| `prometheus-client` | >=0.19 | Metrics |
| `sentry-sdk` | >=2.49.0 | Error tracking |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `python-dotenv` | >=1.0 | Environment variables |
| `tenacity` | >=8.2 | Retry logic |
| `pyyaml` | >=6.0 | YAML parsing |
| `orjson` | >=3.9 | Fast JSON |
| `python-dateutil` | >=2.8 | Date utilities |
| `email-validator` | >=2.1 | Email validation |
| `structlog` | >=25.5.0 | Structured logging |

### 3D & Visual

| Package | Version | Purpose |
|---------|---------|---------|
| `Pillow` | >=10.0 | Image processing |
| `opencv-python` | >=4.8 | Computer vision |

### Performance

| Package | Version | Purpose |
|---------|---------|---------|
| `aiofiles` | >=24.1.0 | Async file I/O |
| `fastapi-cache2` | >=0.2.1 | Caching |
| `redis` | >=5.0 | Redis client |

### ML/AI (Core)

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | >=2.1.3 | Numerical computing |
| `scipy` | >=1.14.1 | Scientific computing |
| `transformers` | >=4.53.0 | Transformer models |
| `sentence-transformers` | >=3.3.1 | Sentence embeddings |
| `tiktoken` | >=0.8.0 | Token counting |
| `chromadb` | >=0.6.0 | Vector database |
| `diffusers` | >=0.33.0 | Diffusion models |

---

## Optional Dependency Groups

### Development (`pip install -e ".[dev]"`)

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >=7.4 | Testing framework |
| `pytest-asyncio` | >=0.23 | Async testing |
| `pytest-cov` | >=4.1 | Coverage |
| `pytest-mock` | >=3.12 | Mocking |
| `mypy` | >=1.8 | Type checking |
| `ruff` | >=0.1 | Linting |
| `black` | >=24.1 | Formatting |
| `isort` | >=5.13 | Import sorting |
| `pre-commit` | >=3.6 | Git hooks |
| `selenium` | >=4.15 | Browser automation |
| `playwright` | >=1.40 | E2E testing |

### ML (`pip install -e ".[ml]"`)

Includes: torch, torchvision, torchaudio, huggingface-hub, pandas, scikit-learn, accelerate, datasets, nltk, spacy, mlflow, bentoml, wandb, tensorboard, matplotlib, seaborn, plotly, librosa, statsmodels, prophet, gymnasium, stable-baselines3, shap, lime, polars, pyarrow, hydra-core, llama-index

### Worker (`pip install -e ".[worker]"`)

| Package | Version | Purpose |
|---------|---------|---------|
| `celery` | >=5.4.0 | Task queue |
| `kombu` | >=5.4.2 | Messaging |
| `flower` | >=2.0.0 | Monitoring |

### Deploy (`pip install -e ".[deploy]"`)

| Package | Version | Purpose |
|---------|---------|---------|
| `gunicorn` | >=23.0.0 | WSGI server |
| `uvicorn[standard]` | >=0.32.1 | ASGI server |

---

## JavaScript/TypeScript Dependencies

**Source**: `package.json`
**Total**: 90 dependencies + 20 devDependencies

### 3D Rendering

| Package | Version | Purpose |
|---------|---------|---------|
| `three` | ^0.182.0 | 3D library |
| `@react-three/fiber` | ^9.5.0 | React Three.js renderer |
| `@react-three/drei` | ^10.7.7 | Three.js helpers |
| `postprocessing` | ^6.38.2 | Post-processing effects |
| `three-stdlib` | ^2.36.1 | Three.js utilities |
| `troika-three-text` | ^0.52.4 | 3D text rendering |
| `@pixiv/three-vrm` | ^3.4.5 | VRM model support |
| `@google/model-viewer` | ^4.1.0 | 3D model viewer |
| `draco3d` | ^1.5.7 | 3D compression |
| `meshoptimizer` | ^1.0.1 | Mesh optimization |

### Animation

| Package | Version | Purpose |
|---------|---------|---------|
| `framer-motion` | ^12.30.0 | React animations |
| `react-spring` | ^10.0.3 | Spring animations |
| `gsap` | ^3.14.2 | Animation library |
| `lottie-web` | ^5.13.0 | Lottie animations |

### Image Processing

| Package | Version | Purpose |
|---------|---------|---------|
| `sharp` | ^0.35.4 | Image processing |
| `pica` | ^9.0.1 | Image resizing |
| `@vercel/og` | ^0.8.6 | OG image generation |

### WordPress Ecosystem

| Package | Version | Purpose |
|---------|---------|---------|
| `@wordpress/scripts` | ^31.4.0 | Build tools |
| `@wordpress/block-editor` | ^15.12.0 | Block editor |
| `@wordpress/components` | ^32.1.0 | UI components |
| `@wordpress/element` | ^6.39.0 | React wrapper |
| `@wordpress/hooks` | ^4.39.0 | Hooks system |
| `@wordpress/api-fetch` | ^7.39.0 | API client |

### WooCommerce

| Package | Version | Purpose |
|---------|---------|---------|
| `@woocommerce/components` | ^13.1.0 | UI components |
| `@woocommerce/data` | ^6.0.0 | Data layer |
| `@woocommerce/settings` | ^1.0.0 | Settings |

### Elementor/UI Libraries

| Package | Version | Purpose |
|---------|---------|---------|
| `swiper` | ^12.1.0 | Slider |
| `aos` | ^2.3.4 | Scroll animations |
| `isotope-layout` | ^3.0.6 | Layout masonry |
| `typed.js` | ^3.0.0 | Typing animation |
| `masonry-layout` | ^4.2.2 | Masonry grid |

### React Ecosystem

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | ^19.2.3 | UI library |
| `react-dom` | ^19.2.3 | DOM renderer |
| `next` | 16.1.6 | React framework |
| `nuxt` | ^4.2.2 | Vue framework |
| `vue` | ^3.5.25 | Vue 3 |

### UI Components

| Package | Version | Purpose |
|---------|---------|---------|
| `@radix-ui/react-label` | ^2.1.8 | Label component |
| `@radix-ui/react-progress` | ^1.1.8 | Progress bar |
| `@radix-ui/react-slot` | ^1.2.4 | Slot component |
| `@radix-ui/react-tabs` | ^1.1.13 | Tabs component |
| `lucide-react` | ^0.562.0 | Icons |
| `class-variance-authority` | ^0.7.1 | CSS variants |
| `clsx` | ^2.1.1 | Classname utility |
| `tailwind-merge` | ^3.4.0 | Tailwind utilities |

### Development Tools

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | ^5.9.3 | Type system |
| `vite` | ^7.2.7 | Build tool |
| `@vitejs/plugin-react` | ^5.1.2 | Vite React plugin |
| `@vitejs/plugin-vue` | ^6.0.3 | Vite Vue plugin |
| `eslint` | ^9.39.2 | Linting |
| `prettier` | ^3.7.4 | Formatting |
| `jest` | ^30.2.0 | Testing |
| `nodemon` | ^3.1.11 | Dev server |

### Monitoring & Error Tracking

| Package | Version | Purpose |
|---------|---------|---------|
| `@sentry/nextjs` | ^10.38.0 | Error tracking |

### Databases & APIs

| Package | Version | Purpose |
|---------|---------|---------|
| `@prisma/client` | ^7.3.0 | Database ORM |
| `prisma` | ^7.1.0 | Schema management |
| `mongodb` | ^7.0.0 | MongoDB client |
| `mongoose` | ^9.0.1 | MongoDB ODM |
| `ioredis` | ^5.8.2 | Redis client |
| `redis` | ^5.10.0 | Redis |

### HTTP & GraphQL

| Package | Version | Purpose |
|---------|---------|---------|
| `axios` | ^1.13.4 | HTTP client |
| `node-fetch` | ^3.3.2 | Fetch API |
| `@apollo/server` | ^5.4.0 | GraphQL server |
| `graphql` | ^16.12.0 | GraphQL |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `dotenv` | ^17.2.3 | Environment variables |
| `joi` | ^18.0.2 | Validation |
| `ajv` | ^8.17.1 | JSON schema |
| `fflate` | ^0.8.2 | Compression |
| `potpack` | ^2.1.0 | Bin packing |

---

## Dependency Management

### Update Dependencies

```bash
# Python
pip install -e ".[all]" --upgrade

# JavaScript
npm update
```

### Security Audits

```bash
# Python
pip-audit

# JavaScript
npm audit
```

### Outdated Check

```bash
# Python
pip list --outdated

# JavaScript
npm outdated
```

---

**See Also**:
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup
- [ENV_VARS_REFERENCE.md](ENV_VARS_REFERENCE.md) - Environment configuration
- [pyproject.toml](../pyproject.toml) - Python dependencies source
- [package.json](../package.json) - JavaScript dependencies source

**Document Owner**: DevSkyy Platform Team
**Next Review**: When dependencies are updated
