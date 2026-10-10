#!/usr/bin/env python3
"""ML audit on the canonical catalog CSV.

Five analyses run from the same loaded data:

  1. Visual clustering (KMeans, k = number of collections)
     - Does the visual structure agree with the human-assigned collection?
     - Disagreement = potential photo / branding bug.

  2. Per-collection outliers (mahalanobis-style distance)
     - Which SKU in each collection is visually most unlike its peers?
     - Top outlier per collection is the prime candidate for re-shoot.

  3. Cross-modal name-image alignment
     - For each SKU, score CLIP cosine(image, name).
     - Lowest-scoring SKUs have a NAME that doesn't match the IMAGE
       (typo, wrong photo attached, etc.) — data integrity bugs.

  4. Top-5 visually similar SKUs per SKU (for the recs widget)
     - Drives the [skyyrose_visual_similar] shortcode you already shipped.

  5. Anomaly detection: any SKU whose nearest neighbor is in a
     DIFFERENT collection. May be intentional (cross-collection
     callbacks) or accidental (mis-tagged).

Output:
  tasks/catalog-ml-report.md   — human-readable
  tasks/catalog-ml-report.json — machine-readable

Embeddings source:
  wordpress-theme/skyyrose-flagship/data/product-embeddings.json
  (CLIP-base, 33 SKUs × 512-d, already L2-normalized)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sklearn.cluster import KMeans  # noqa: E402
from sklearn.metrics import silhouette_score  # noqa: E402

from skyyrose.core import clip_embedder  # noqa: E402
from skyyrose.core.catalog_loader import read_catalog_rows  # noqa: E402
from skyyrose.core.paths import THEME_ROOT, WP_PRODUCTS_DIR  # noqa: E402

EMBEDDINGS_PATH = THEME_ROOT / "data" / "product-embeddings.json"
PRODUCTS_DIR = WP_PRODUCTS_DIR


def _load_embeddings_matrix() -> tuple[list[str], np.ndarray, dict[str, dict]]:
    payload = json.loads(EMBEDDINGS_PATH.read_text())
    products = payload["products"]
    skus = sorted(products.keys())
    matrix = np.stack([np.asarray(products[s]["embedding"], dtype=np.float32) for s in skus])
    return skus, matrix, products


def _attach_catalog(products: dict[str, dict]) -> dict[str, dict]:
    """Merge catalog rows into the embeddings dict by SKU."""
    catalog = {row["sku"]: row for row in read_catalog_rows()}
    for sku, p in products.items():
        if sku in catalog:
            p["catalog"] = catalog[sku]
    return products


# ---------------------------------------------------------------------------
# 1. Visual clustering vs collections
# ---------------------------------------------------------------------------


def cluster_vs_collections(skus: list[str], matrix: np.ndarray, products: dict) -> dict:
    collections = sorted({products[s]["collection"] for s in skus})
    k = len(collections)
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(matrix)
    sil = silhouette_score(matrix, km.labels_)

    # Cross-tab cluster assignment vs human collection label.
    # Each cluster gets named by the most common collection in it.
    cluster_to_collection: dict[int, str] = {}
    for cluster_id in range(k):
        members = [skus[i] for i, c in enumerate(km.labels_) if c == cluster_id]
        coll_counts: dict[str, int] = defaultdict(int)
        for sku in members:
            coll_counts[products[sku]["collection"]] += 1
        cluster_to_collection[cluster_id] = max(coll_counts, key=coll_counts.get)

    disagreements = []
    for i, sku in enumerate(skus):
        cluster = int(km.labels_[i])
        human_collection = products[sku]["collection"]
        ml_collection = cluster_to_collection[cluster]
        if human_collection != ml_collection:
            disagreements.append(
                {
                    "sku": sku,
                    "name": products[sku]["name"],
                    "human_collection": human_collection,
                    "ml_collection_guess": ml_collection,
                    "cluster_id": cluster,
                }
            )

    return {
        "k": k,
        "silhouette": float(sil),
        "cluster_to_collection": cluster_to_collection,
        "disagreements": disagreements,
        "labels": {sku: int(km.labels_[i]) for i, sku in enumerate(skus)},
    }


# ---------------------------------------------------------------------------
# 2. Per-collection outliers
# ---------------------------------------------------------------------------


def per_collection_outliers(skus: list[str], matrix: np.ndarray, products: dict) -> list[dict]:
    # Group by collection
    by_coll: dict[str, list[int]] = defaultdict(list)
    for i, sku in enumerate(skus):
        by_coll[products[sku]["collection"]].append(i)

    outliers: list[dict] = []
    for collection, indices in by_coll.items():
        if len(indices) < 2:
            continue
        cluster_vecs = matrix[indices]
        centroid = cluster_vecs.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        # Lower cosine = more outlying.
        sims = cluster_vecs @ centroid
        worst_idx = int(np.argmin(sims))
        outliers.append(
            {
                "collection": collection,
                "outlier_sku": skus[indices[worst_idx]],
                "outlier_name": products[skus[indices[worst_idx]]]["name"],
                "cosine_to_collection_centroid": float(sims[worst_idx]),
                "best_in_collection_cosine": float(sims.max()),
                "size": len(indices),
            }
        )
    outliers.sort(key=lambda o: o["cosine_to_collection_centroid"])
    return outliers


# ---------------------------------------------------------------------------
# 3. Cross-modal name-vs-image alignment
# ---------------------------------------------------------------------------


def name_image_alignment(skus: list[str], matrix: np.ndarray, products: dict) -> list[dict]:
    """Score CLIP(name_text, image_embedding) for each SKU.

    Low score = name doesn't match the image. Useful for catching:
      - SKU named "X Hoodie" with a product photo of a tee
      - typos in product names
      - mis-attached images at intake
    """
    results = []
    for i, sku in enumerate(skus):
        name = products[sku]["name"]
        text_vec = clip_embedder.embed_text(name)
        score = float(np.dot(text_vec, matrix[i]))
        results.append(
            {
                "sku": sku,
                "name": name,
                "collection": products[sku]["collection"],
                "name_image_cosine": score,
            }
        )
    results.sort(key=lambda r: r["name_image_cosine"])
    return results


# ---------------------------------------------------------------------------
# 4. Top-5 similar SKUs per SKU
# ---------------------------------------------------------------------------


def top_n_similar(
    skus: list[str], matrix: np.ndarray, products: dict, n: int = 5
) -> dict[str, list[dict]]:
    sims = matrix @ matrix.T  # (N, N), L2-normalized so cosine = dot
    out: dict[str, list[dict]] = {}
    for i, sku in enumerate(skus):
        ranked = np.argsort(-sims[i])
        ranked = [j for j in ranked if j != i][:n]
        out[sku] = [
            {
                "sku": skus[j],
                "name": products[skus[j]]["name"],
                "collection": products[skus[j]]["collection"],
                "score": float(sims[i, j]),
            }
            for j in ranked
        ]
    return out


# ---------------------------------------------------------------------------
# 5. Cross-collection nearest neighbors
# ---------------------------------------------------------------------------


def cross_collection_anomalies(skus: list[str], matrix: np.ndarray, products: dict) -> list[dict]:
    sims = matrix @ matrix.T
    np.fill_diagonal(sims, -2.0)
    anomalies = []
    for i, sku in enumerate(skus):
        nearest = int(np.argmax(sims[i]))
        if products[sku]["collection"] != products[skus[nearest]]["collection"]:
            anomalies.append(
                {
                    "sku": sku,
                    "name": products[sku]["name"],
                    "sku_collection": products[sku]["collection"],
                    "nearest_sku": skus[nearest],
                    "nearest_name": products[skus[nearest]]["name"],
                    "nearest_collection": products[skus[nearest]]["collection"],
                    "score": float(sims[i, nearest]),
                }
            )
    anomalies.sort(key=lambda a: -a["score"])
    return anomalies


# ---------------------------------------------------------------------------
# Markdown emitter
# ---------------------------------------------------------------------------


def emit_markdown(results: dict) -> str:
    lines: list[str] = []
    lines.append("# Catalog ML Audit Report")
    lines.append("")
    lines.append(f"- SKUs analysed: **{results['n_skus']}**")
    lines.append(f"- Collections: {', '.join(results['collections'])}")
    lines.append(f"- Embedding model: `{results['model']}` ({results['dim']}-d)")
    lines.append("")

    # 1. Clustering
    c = results["clustering"]
    lines.append(f"## 1. Visual clustering vs collections (k={c['k']})")
    lines.append("")
    lines.append(
        f"- **Silhouette score:** {c['silhouette']:.4f} "
        f"(higher = clusters more separable; >0.5 is strong)"
    )
    lines.append(
        f"- **Disagreements:** {len(c['disagreements'])} SKUs land in a cluster "
        f"whose dominant collection is NOT the SKU's collection."
    )
    lines.append("")
    if c["disagreements"]:
        lines.append("| sku | name | tagged | ML guess |")
        lines.append("|-----|------|--------|----------|")
        for d in c["disagreements"]:
            lines.append(
                f"| `{d['sku']}` | {d['name']} | {d['human_collection']} | "
                f"**{d['ml_collection_guess']}** |"
            )
        lines.append("")

    # 2. Outliers
    lines.append("## 2. Per-collection visual outliers")
    lines.append("")
    lines.append("Lowest cosine to its collection centroid = most visually unlike its peers.")
    lines.append("")
    lines.append("| collection | size | outlier sku | name | cosine | best |")
    lines.append("|-----------|-----:|-------------|------|-------:|-----:|")
    for o in results["outliers"]:
        lines.append(
            f"| {o['collection']} | {o['size']} | `{o['outlier_sku']}` | "
            f"{o['outlier_name']} | {o['cosine_to_collection_centroid']:.3f} | "
            f"{o['best_in_collection_cosine']:.3f} |"
        )
    lines.append("")

    # 3. Name-image alignment
    lines.append("## 3. Name vs image alignment (lowest = potential mis-attached image)")
    lines.append("")
    lines.append("CLIP cosine between the product NAME (text) and its IMAGE (vision).")
    lines.append("Low score = name and image are about different things.")
    lines.append("")
    lines.append("| sku | collection | name | cosine |")
    lines.append("|-----|-----------|------|-------:|")
    for r in results["name_image"][:15]:
        lines.append(
            f"| `{r['sku']}` | {r['collection']} | {r['name']} | {r['name_image_cosine']:.3f} |"
        )
    lines.append(f"\n_(showing 15 lowest of {len(results['name_image'])} total)_")
    lines.append("")

    # 4. Cross-collection anomalies
    lines.append("## 4. Cross-collection nearest-neighbor anomalies")
    lines.append("")
    lines.append("SKUs whose nearest visual neighbor is in a *different* collection.")
    lines.append("Could be intentional (cross-collection callbacks) or a tagging error.")
    lines.append("")
    if results["cross_collection"]:
        lines.append("| sku | tagged | nearest sku | nearest collection | score |")
        lines.append("|-----|--------|-------------|--------------------|------:|")
        for a in results["cross_collection"]:
            lines.append(
                f"| `{a['sku']}` | {a['sku_collection']} | `{a['nearest_sku']}` | "
                f"**{a['nearest_collection']}** | {a['score']:.3f} |"
            )
        lines.append("")

    # 5. Top-5 (compact)
    lines.append("## 5. Top-5 visually similar SKUs (drives the /shortcode widget)")
    lines.append("")
    lines.append("Sample (first 6 SKUs, full set in JSON):")
    lines.append("")
    sample = list(results["top_similar"].items())[:6]
    for sku, neighbors in sample:
        names = ", ".join(f"`{n['sku']}` ({n['score']:.2f})" for n in neighbors[:3])
        lines.append(f"- **`{sku}`** → {names}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", type=Path, default=ROOT / "tasks/catalog-ml-report.md")
    parser.add_argument("--output-json", type=Path, default=ROOT / "tasks/catalog-ml-report.json")
    args = parser.parse_args()

    if not EMBEDDINGS_PATH.exists():
        print(f"FATAL: embeddings not found: {EMBEDDINGS_PATH}", file=sys.stderr)
        return 2

    print(f"Loading embeddings from {EMBEDDINGS_PATH.relative_to(ROOT)}...")
    skus, matrix, products = _load_embeddings_matrix()
    products = _attach_catalog(products)
    print(f"  {len(skus)} SKUs × {matrix.shape[1]} dims")

    print("Running 5 analyses...")
    payload = json.loads(EMBEDDINGS_PATH.read_text())
    results = {
        "n_skus": len(skus),
        "collections": sorted({products[s]["collection"] for s in skus}),
        "model": payload.get("model", "unknown"),
        "dim": payload.get("dim", matrix.shape[1]),
        "clustering": cluster_vs_collections(skus, matrix, products),
        "outliers": per_collection_outliers(skus, matrix, products),
        "name_image": name_image_alignment(skus, matrix, products),
        "top_similar": top_n_similar(skus, matrix, products, n=5),
        "cross_collection": cross_collection_anomalies(skus, matrix, products),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(results, indent=2))
    args.output_md.write_text(emit_markdown(results))

    print()
    print(f"Wrote {args.output_md.relative_to(ROOT)}")
    print(f"Wrote {args.output_json.relative_to(ROOT)}")
    print()
    print(f"  silhouette: {results['clustering']['silhouette']:.3f}")
    print(f"  cluster disagreements: {len(results['clustering']['disagreements'])}")
    print(f"  cross-collection anomalies: {len(results['cross_collection'])}")
    print(
        f"  weakest name-image score: {results['name_image'][0]['sku']} "
        f"({results['name_image'][0]['name_image_cosine']:.3f})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
