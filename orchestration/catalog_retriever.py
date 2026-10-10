"""CatalogRetriever — semantic retrieval over the SkyyRose canonical catalog.

Thin wrapper over the existing orchestration stack:

- orchestration.embedding_engine — Sentence Transformers (local, free)
- orchestration.vector_store     — ChromaDB by default; Pinecone available
- skyyrose.core.catalog_loader   — canonical CSV reader
- orchestration.brand_context    — CatalogContext + load_catalog_context

The retriever indexes `branding_spec + description + name` per SKU and serves
semantic queries for agents that need "find SKUs similar to this query" or
"surface this collection's thematic matches" at runtime. ChromaDB is default
because the 30-SKU catalog is trivially small; Pinecone swap is a one-line
config change via VectorStoreConfig.

Everything is async because the underlying engines are async.
"""

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from orchestration.brand_context import CatalogSummary, load_catalog_context
from orchestration.embedding_engine import (
    BaseEmbeddingEngine,
    EmbeddingConfig,
    EmbeddingProvider,
    create_embedding_engine,
)
from orchestration.vector_store import (
    BaseVectorStore,
    Document,
    SearchResult,
    VectorDBType,
    VectorStoreConfig,
    create_vector_store,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CatalogMatch:
    """A single SKU match from semantic search, scored against a query."""

    sku: str
    name: str
    collection: str
    score: float
    branding_spec: str
    description: str


@dataclass(frozen=True)
class CatalogAnswer:
    """A natural-language answer over the catalog, with cited SKUs.

    Returned by ``CatalogRetriever.answer_question()``. The ``citations`` list
    is the union of (a) SKUs the LLM explicitly bracketed in its answer text
    and (b) the retrieved matches the LLM was given as context. Callers that
    want strict "only what the LLM cited" can iterate ``answer`` and parse
    [SKU] markers themselves; the answer text preserves them verbatim.
    """

    question: str
    answer: str
    citations: list[str]  # SKUs cited in the answer text (in order of first mention)
    matches: list[CatalogMatch]  # The full retrieval context the LLM saw
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


# Regex for extracting [SKU] citation markers from the LLM's answer.
# SKUs are lowercase letters/digits/hyphen, e.g. [br-005], [kids-002].
_CITATION_PATTERN = re.compile(r"\[([a-z]{2,5}-[a-z0-9]+)\]")


def _extract_citations(text: str) -> list[str]:
    """Pull [sku-NNN] markers from an answer string.

    Returns SKUs in order of first appearance, deduplicated. Used by both the
    blocking ``answer_question`` and the streaming ``answer_question_stream``
    paths so citation parsing stays consistent across the two surfaces.
    """
    seen: set[str] = set()
    citations: list[str] = []
    for sku in _CITATION_PATTERN.findall(text):
        if sku not in seen:
            seen.add(sku)
            citations.append(sku)
    return citations


class CatalogRetriever:
    """Semantic index + retrieval over the SkyyRose canonical catalog.

    Usage:
        retriever = CatalogRetriever()
        await retriever.initialize()
        await retriever.index_catalog()
        matches = await retriever.retrieve("distressed denim jackets", top_k=5)

    Index key: `branding_spec + description + name`. Metadata carries
    `sku`, `collection`, and `price` so callers can post-filter without
    re-querying the CSV.
    """

    DEFAULT_COLLECTION = "skyyrose-catalog-v1"

    def __init__(
        self,
        embedding_engine: BaseEmbeddingEngine | None = None,
        vector_store: BaseVectorStore | None = None,
        collection_name: str | None = None,
        namespace: str | None = "catalog",
    ) -> None:
        """
        Args:
            embedding_engine: Override the default Sentence Transformers engine
                (e.g. pass a configured VoyageEmbeddingEngine for production).
            vector_store: Override the default ChromaDB store
                (e.g. pass a Pinecone store for production).
            collection_name: Override the Chroma collection name.
            namespace: Logical partition within the index. Defaults to "catalog";
                pass `None` to write/read in the default partition.
        """
        self._embedder = embedding_engine
        self._store = vector_store
        self._collection_name = collection_name or self.DEFAULT_COLLECTION
        self._namespace = namespace
        self._initialized = False

    async def initialize(self) -> None:
        """Lazy-create engine + store if not injected; init both."""
        if self._embedder is None:
            self._embedder = create_embedding_engine(
                EmbeddingConfig(provider=EmbeddingProvider.SENTENCE_TRANSFORMERS)
            )
        await self._embedder.initialize()

        if self._store is None:
            self._store = create_vector_store(
                VectorStoreConfig(
                    db_type=VectorDBType.CHROMADB,
                    collection_name=self._collection_name,
                )
            )
        await self._store.initialize()
        self._initialized = True

    async def index_catalog(self, *, dry_run: bool = False) -> dict[str, Any]:
        """Embed + upsert every SKU in the canonical catalog.

        Each SKU's content is composed from its CSV row PLUS its per-product
        dossier markdown (technique, color, embroidery placement, scene
        setting). SKUs without a dossier (retired, or not yet authored) are
        skipped and listed in `manifest['skipped_skus']` rather than failing
        the run — call sites can decide whether the skip set is acceptable.

        Args:
            dry_run: when True, skip the upsert and return the count + sample
                     so callers can preview cost/work before committing.

        Returns:
            Manifest dict: {total_skus, indexed_ids, skipped_skus, dry_run,
            sample_ids, namespace}
        """
        self._require_init()
        rows = self._catalog_rows()

        # Lazy import — keeps skyyrose.core optional at module load
        try:
            from skyyrose.core.dossier_loader import (
                DossierMissingError,
                get_product_with_dossier,
            )
        except ImportError as exc:
            raise RuntimeError(
                f"CatalogRetriever now requires skyyrose.core.dossier_loader. Import failed: {exc}"
            ) from exc

        documents: list[Document] = []
        texts: list[str] = []
        skipped: list[dict[str, str]] = []

        for row in rows:
            sku = (row.get("sku") or "").strip()
            try:
                merged = get_product_with_dossier(sku)
            except (DossierMissingError, KeyError) as exc:
                logger.info("Skipping %s: %s", sku, exc)
                skipped.append({"sku": sku, "reason": type(exc).__name__})
                continue

            dossier_data = merged.get("dossier", {})
            content = self._compose_content(row, dossier_data)
            doc = Document(
                id=f"sku:{sku}",
                content=content,
                metadata={
                    "sku": sku,
                    "name": (row.get("name") or "").strip(),
                    "collection": (row.get("collection") or "").strip().lower(),
                    "price": (row.get("price") or "").strip(),
                    "badge": (row.get("badge") or "").strip(),
                    "published": (row.get("published") or "").strip() == "1",
                    "garment_type_lock": (dossier_data.get("garment_type_lock") or "").strip(),
                    "branding_block": (dossier_data.get("branding_block") or "").strip(),
                    "description": (row.get("description") or "").strip(),
                },
                source="wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv",
            )
            documents.append(doc)
            texts.append(content)

        manifest: dict[str, Any] = {
            "total_skus": len(documents),
            "dry_run": dry_run,
            "sample_ids": [d.id for d in documents[:5]],
            "indexed_ids": [],
            "skipped_skus": skipped,
            "namespace": self._namespace,
        }

        if dry_run or not documents:
            logger.info(
                "CatalogRetriever.index_catalog: %s mode, %d docs prepared, %d skipped",
                "DRY-RUN" if dry_run else "EMPTY",
                len(documents),
                len(skipped),
            )
            return manifest

        assert self._embedder is not None and self._store is not None
        embeddings = await self._embedder.embed_batch(texts)
        ids = await self._store.add_documents(documents, embeddings, namespace=self._namespace)
        manifest["indexed_ids"] = ids
        logger.info(
            "CatalogRetriever.index_catalog: indexed %d SKUs into %s (ns=%s, skipped=%d)",
            len(ids),
            self._collection_name,
            self._namespace,
            len(skipped),
        )
        return manifest

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        collection: str | None = None,
    ) -> list[CatalogMatch]:
        """Return the top-k SKUs semantically matching ``query``.

        Args:
            query: free-form natural language (e.g. "gothic luxury silver hoodie")
            top_k: max matches to return (default 5)
            collection: optional collection-slug filter (e.g. "black-rose")
        """
        self._require_init()
        assert self._embedder is not None and self._store is not None

        query_embedding = await self._embedder.embed_query(query)
        filter_metadata = {"collection": collection} if collection else None
        results = await self._store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
            namespace=self._namespace,
        )
        return [self._match_from_result(r) for r in results]

    async def retrieve_by_collection(self, slug: str, *, top_k: int = 5) -> list[CatalogMatch]:
        """Shorthand for scoping a generic query to a single collection."""
        return await self.retrieve(
            query=f"{slug} collection signature pieces", top_k=top_k, collection=slug
        )

    async def find_similar_by_sku(self, sku: str, *, top_k: int = 5) -> list[CatalogMatch]:
        """Return the top-k SKUs semantically nearest to ``sku`` (excluding itself).

        Re-embeds the source SKU's composed content via Voyage and queries the
        vector store, then filters the source SKU from the result set. Costs
        one Voyage query embedding per call (~$0.0001).

        We pull `top_k + 1` from the store so dropping the source still leaves
        ``top_k`` results in the common case where the source itself is the
        top match.

        Raises:
            KeyError if ``sku`` is not in the canonical catalog.
            DossierMissingError if the SKU's dossier markdown file is absent.
        """
        self._require_init()
        assert self._embedder is not None and self._store is not None

        # Lazy import — keeps skyyrose.core optional at module load
        from skyyrose.core.dossier_loader import get_product_with_dossier

        merged = get_product_with_dossier(sku)
        content = self._compose_content(merged, merged.get("dossier", {}))

        # Pull one extra to absorb the source SKU itself (which usually scores 1.0).
        # MUST pass namespace=self._namespace — the catalog lives in the "catalog"
        # namespace, and querying the default partition silently returns nothing.
        query_embedding = await self._embedder.embed_query(content)
        results = await self._store.search(
            query_embedding=query_embedding,
            top_k=top_k + 1,
            namespace=self._namespace,
        )

        matches: list[CatalogMatch] = []
        for r in results:
            match = self._match_from_result(r)
            if match.sku == sku:
                continue
            matches.append(match)
            if len(matches) >= top_k:
                break
        return matches

    # Default model for catalog Q&A. Haiku 4.5 is the sweet spot:
    # ~$1/MTok input, ~$5/MTok output, fast, plenty of capability for grounded
    # short-form answers. Override with answer_question(model=...) if needed.
    DEFAULT_QA_MODEL = "claude-haiku-4-5-20251001"

    QA_SYSTEM_PROMPT = (
        "You are a knowledgeable concierge for SkyyRose, a luxury streetwear brand. "
        "The brand has 4 collections: "
        "Black Rose (gothic Oakland), Love Hurts (passionate, Beauty-and-the-Beast), "
        "Signature (SF Bay Area, golden hour), and Kids Capsule. "
        "Answer the user's question using ONLY the catalog excerpts provided. "
        "Cite specific products by their SKU in square brackets like [br-005] when "
        "they're directly relevant. If the catalog excerpts don't contain enough "
        "information to answer, say so honestly — don't invent products, prices, or "
        "details that aren't in the excerpts. Keep answers conversational and concise "
        "(2-4 sentences typically; longer only if the question genuinely needs it)."
    )

    async def answer_question(
        self,
        question: str,
        *,
        top_k: int = 5,
        model: str | None = None,
        max_tokens: int = 400,
        anthropic_client: Any | None = None,
    ) -> CatalogAnswer:
        """Answer a natural-language question grounded in the SkyyRose catalog.

        Pipeline: Voyage query embed → Pinecone retrieve top-k → Claude Haiku
        synthesizes a grounded answer with [SKU] citations.

        Args:
            question: free-form natural-language question
            top_k: how many matches to surface as context (default 5)
            model: Claude model id (default: ``DEFAULT_QA_MODEL``)
            max_tokens: cap on answer length
            anthropic_client: inject a pre-built ``anthropic.AsyncAnthropic`` for
                testing; production callers leave this None to lazy-create one.

        Cost (rough, per request): ~$0.0001 Voyage + ~$0.001-0.002 Haiku
        depending on context length and answer length.
        """
        self._require_init()

        matches = await self.retrieve(question, top_k=top_k)
        user_prompt = self._build_qa_prompt(question, matches)
        chosen_model = model or self.DEFAULT_QA_MODEL
        client = self._get_anthropic_client(anthropic_client)

        response = await client.messages.create(
            model=chosen_model,
            max_tokens=max_tokens,
            system=self.QA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Extract text + parse citations
        answer_text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        citations = _extract_citations(answer_text)

        usage = getattr(response, "usage", None)
        return CatalogAnswer(
            question=question,
            answer=answer_text.strip(),
            citations=citations,
            matches=matches,
            model=chosen_model,
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
        )

    async def answer_question_stream(
        self,
        question: str,
        *,
        top_k: int = 5,
        model: str | None = None,
        max_tokens: int = 400,
        anthropic_client: Any | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream a grounded answer as a sequence of structured events.

        Yields, in order:
            1. ``{"type": "matches", "matches": [{...}, ...]}`` — citations
               and full match metadata before any text arrives
            2. ``{"type": "text", "delta": "..."}`` — incremental text deltas
               as Claude produces them
            3. ``{"type": "done", "citations": [...], "input_tokens": N,
                "output_tokens": M, "model": "..."}`` — final metadata once
               the stream ends; citations are parsed from accumulated text

        First-token latency is typically 200-400ms (vs ~3s for the non-streaming
        ``answer_question``). Total cost is the same — streaming is purely a
        latency/UX win, not a cost win.
        """
        self._require_init()

        matches = await self.retrieve(question, top_k=top_k)

        # Emit matches up-front so the UI can render citations before text.
        # branding_spec/description are truncated to the same budgets the
        # LLM prompt uses — sending the full ~3KB dossier branding_block
        # over the SSE wire wastes bandwidth (and clients only render a
        # short preview anyway).
        yield {
            "type": "matches",
            "matches": [
                {
                    "sku": m.sku,
                    "name": m.name,
                    "collection": m.collection,
                    "score": m.score,
                    "description": m.description[:400],
                    "branding_spec": m.branding_spec[:1500],
                }
                for m in matches
            ],
        }

        user_prompt = self._build_qa_prompt(question, matches)
        chosen_model = model or self.DEFAULT_QA_MODEL
        client = self._get_anthropic_client(anthropic_client)

        accumulated = ""
        async with client.messages.stream(
            model=chosen_model,
            max_tokens=max_tokens,
            system=self.QA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for delta in stream.text_stream:
                accumulated += delta
                yield {"type": "text", "delta": delta}

            final = await stream.get_final_message()

        usage = getattr(final, "usage", None)
        yield {
            "type": "done",
            "citations": _extract_citations(accumulated),
            "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
            "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
            "model": chosen_model,
        }

    def _build_qa_prompt(self, question: str, matches: list[CatalogMatch]) -> str:
        """Compose the user-side RAG prompt from question + retrieved matches.

        Per-match budgets are deliberately generous: SkyyRose dossier
        branding_blocks routinely run 1500-3000 chars (Front/Back/Sleeves/Hood
        sections with technique/color/position per placement). A 300-char
        truncation lost detail past the first paragraph (e.g. hood interior
        linings, sleeve placements) and forced the LLM to say "I don't have
        that information" when the dossier in fact did. With top_k≤10 and
        ~1800 chars/match, total context is ~18KB ≈ 4500 tokens — well within
        Haiku's 200K context, ~$0.0045 input cost at most.
        """
        if not matches:
            return (
                f"Question: {question}\n\n"
                f"No catalog excerpts were retrieved for this question. "
                f"Tell the user clearly that you don't have product information that matches "
                f"their query, without inventing any details."
            )

        blocks: list[str] = []
        for m in matches:
            # The "===" rule is a strong attention separator that helps the LLM
            # keep facts from different products from bleeding together.
            block = (
                f"=== [{m.sku}] {m.name} (collection: {m.collection}) ===\n"
                f"BRANDING SPEC:\n{m.branding_spec[:1500].strip()}"
            )
            if m.description:
                block += f"\n\nDESCRIPTION: {m.description[:400].strip()}"
            blocks.append(block)
        context = "\n\n".join(blocks)
        return (
            f"Question: {question}\n\n"
            f"Catalog excerpts ({len(matches)} most relevant SKUs, ranked by similarity):\n\n"
            f"{context}\n\n"
            f"=== END OF CATALOG EXCERPTS ===\n\n"
            f"Answer the question using ONLY the information above. Cite SKUs in [brackets] "
            f"like [br-005] when you reference a specific product. If the information "
            f"needed is not in the excerpts, say so honestly."
        )

    @staticmethod
    def _get_anthropic_client(injected: Any | None) -> Any:
        """Return ``injected`` if non-None, else lazy-construct an AsyncAnthropic.

        Lazy import keeps anthropic optional at module-load time and avoids
        opening a real client when callers (typically tests) inject a mock.
        """
        if injected is not None:
            return injected
        import anthropic

        return anthropic.AsyncAnthropic()

    def get_info(self) -> dict[str, Any]:
        """Public diagnostic snapshot — embedder + namespace.

        Replaces direct access to `_embedder`/`_namespace` from outside the class
        (used by /catalog/health and similar liveness endpoints).
        """
        return {
            "embedder": self._embedder.get_info() if self._embedder else None,
            "namespace": self._namespace,
            "initialized": self._initialized,
        }

    async def close(self) -> None:
        if self._store is not None:
            await self._store.close()
        self._initialized = False

    # -- helpers --

    def _catalog_rows(self) -> list[dict[str, str]]:
        """Read catalog via the shared loader; fall back to stdlib csv."""
        try:
            from skyyrose.core.catalog_loader import read_catalog_rows

            return read_catalog_rows()
        except ImportError:
            context = load_catalog_context()  # uses brand_context's fallback path
            # brand_context collapses per-row data into summaries, so when
            # skyyrose.core is unavailable we can't faithfully reconstruct
            # individual rows. Raise rather than index a degenerate view.
            raise RuntimeError(
                "CatalogRetriever requires skyyrose.core.catalog_loader. "
                f"Observed {len(context.summaries)} collection summaries via "
                "orchestration.brand_context, but SKU-level rows are unavailable."
            )

    @staticmethod
    def _compose_content(row: dict[str, str], dossier_data: dict[str, str]) -> str:
        """Compose semantic content from CSV row + parsed dossier.

        Dossier fields carry the high-signal content (technique, color,
        embroidery placement, scene context); CSV fields anchor the product
        identity (name, collection, price tier). The dossier's `negative_block`
        is intentionally OMITTED — it describes what NOT to render and would
        pollute similarity scoring (a query like "no chest logo" would otherwise
        be drawn to negative-block-rich documents).
        """
        parts: list[str] = []
        name = (row.get("name") or "").strip()
        collection = (row.get("collection") or "").strip()
        description = (row.get("description") or "").strip()

        if name:
            parts.append(f"Product: {name}")
        if collection:
            parts.append(f"Collection: {collection}")

        garment_lock = (dossier_data.get("garment_type_lock") or "").strip()
        if garment_lock:
            parts.append(f"Garment: {garment_lock}")

        branding = (dossier_data.get("branding_block") or "").strip()
        if branding:
            parts.append(f"Branding:\n{branding}")

        setting = (dossier_data.get("scene_setting") or "").strip()
        if setting:
            parts.append(f"Setting: {setting}")

        if description:
            parts.append(description)

        return "\n".join(parts)

    @staticmethod
    def _match_from_result(result: SearchResult) -> CatalogMatch:
        meta = result.document.metadata
        return CatalogMatch(
            sku=meta.get("sku", ""),
            name=meta.get("name", ""),
            collection=meta.get("collection", ""),
            score=result.score,
            # Prefer the rich dossier branding_block; fall back to legacy CSV
            # branding_spec for any pre-existing index entries.
            branding_spec=meta.get("branding_block") or meta.get("branding_spec", ""),
            description=meta.get("description", ""),
        )

    @classmethod
    async def for_production(
        cls,
        *,
        namespace: str | None = "catalog",
        pinecone_index: str | None = None,
    ) -> CatalogRetriever:
        """Pre-configured retriever using Voyage 3-large + Pinecone serverless.

        Reads PINECONE_API_KEY and VOYAGE_API_KEY from environment. Creates the
        Pinecone index if it does not exist (dimension 1024 for voyage-3-large).

        Returns an already-initialized retriever — call sites can go straight
        to `index_catalog()` or `retrieve()` without an extra `initialize()`.
        """
        import os

        embedding = create_embedding_engine(EmbeddingConfig(provider=EmbeddingProvider.VOYAGE))
        await embedding.initialize()

        store = create_vector_store(
            VectorStoreConfig(
                db_type=VectorDBType.PINECONE,
                pinecone_index_name=pinecone_index or os.getenv("PINECONE_INDEX_NAME", "skyyrose"),
                dimension=embedding.dimension or 1024,
            )
        )
        await store.initialize()

        retriever = cls(
            embedding_engine=embedding,
            vector_store=store,
            namespace=namespace,
        )
        retriever._initialized = True
        return retriever

    def _require_init(self) -> None:
        if not self._initialized:
            raise RuntimeError("CatalogRetriever not initialized — await initialize() first.")


__all__ = [
    "CatalogMatch",
    "CatalogRetriever",
    "CatalogSummary",  # re-exported for one-stop import
]
