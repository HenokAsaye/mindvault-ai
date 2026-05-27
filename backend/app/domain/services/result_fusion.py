from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.domain.value_objects.document import Document
from app.domain.services.score_normalizer import normalize_scores


def fuse_results(
    vector_results: List[Document],
    key_results: List[Document],
    fusion_weights: Optional[Dict[str, float]] = None,
    top_k: int = 5,
    normalization_method: str = "softmax",
) -> List[Document]:

    if fusion_weights is None:
        fusion_weights = {"vector": 0.6, "key": 0.4}

    if "vector" not in fusion_weights or "key" not in fusion_weights:
        raise ValueError("fusion_weights must have 'vector' and 'key' keys")

    # Normalize fusion weights to sum to 1
    total_weight = fusion_weights["vector"] + fusion_weights["key"]
    w_vec = fusion_weights["vector"] / total_weight
    w_key = fusion_weights["key"] / total_weight

    # Step 1: Extract and normalize scores per strategy independently
    vec_scores = [doc.score for doc in vector_results]
    key_scores = [doc.score for doc in key_results]

    vec_normalized = (
        normalize_scores(vec_scores, method=normalization_method) if vec_scores else []
    )
    key_normalized = (
        normalize_scores(key_scores, method=normalization_method) if key_scores else []
    )

    candidates: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "document": None,
            "vector_score_norm": 0.0,
            "key_score_norm": 0.0,
            "sources": [],
        }
    )

    for i, doc in enumerate(vector_results):
        candidates[doc.id]["document"] = doc
        candidates[doc.id]["vector_score_norm"] = vec_normalized[i]
        candidates[doc.id]["sources"].append("vector")

    for i, doc in enumerate(key_results):
        if doc.id not in candidates:
            candidates[doc.id]["document"] = doc
        candidates[doc.id]["key_score_norm"] = key_normalized[i]
        if "key" not in candidates[doc.id]["sources"]:
            candidates[doc.id]["sources"].append("key")

    fused_docs = []
    for doc_id, candidate in candidates.items():
        doc = candidate["document"]
        fused_score = (
            w_vec * candidate["vector_score_norm"] + w_key * candidate["key_score_norm"]
        )

        # Create new document with fused score
        fused_doc = Document(
            id=doc.id,
            text=doc.text,
            score=fused_score,
            source="hybrid",
            metadata=doc.metadata,
            vector_score=doc.vector_score,
            key_score=doc.key_score,
            rerank_score=None,
            retrieval_sources=candidate["sources"],
        )
        fused_docs.append(fused_doc)

    # Step 4: Sort by fused score (descending) and return top-K
    fused_docs.sort(key=lambda d: d.score, reverse=True)
    return fused_docs[:top_k]


def remove_duplicates(
    documents: List[Document],
    keep_first: bool = True,
) -> List[Document]:
    seen: Dict[str, Document] = {}

    for doc in documents:
        if doc.id not in seen:
            seen[doc.id] = doc
        elif not keep_first and doc.score > seen[doc.id].score:
            seen[doc.id] = doc

    return list(seen.values())


def apply_reciprocal_rank_fusion(
    vector_results: List[Document],
    key_results: List[Document],
    k: int = 60,  # Standard RRF parameter
    top_k: int = 5,
) -> List[Document]:
    """Fuse using Reciprocal Rank Fusion (RRF) formula.

    RRF score: 1 / (k + rank)
    This is an alternative to weighted fusion that doesn't require normalization.

    Args:
        vector_results: Ranked documents from vector search.
        key_results: Ranked documents from keyword search.
        k: RRF parameter (typically 60). Controls decay rate.
        top_k: Number of results to return.

    Returns:
        Fused documents using RRF scoring.
    """
    rrf_scores: Dict[str, float] = {}
    sources: Dict[str, set] = defaultdict(set)
    doc_map: Dict[str, Document] = {}

    # Calculate RRF scores for vector results
    for rank, doc in enumerate(vector_results, start=1):
        rrf_scores[doc.id] = rrf_scores.get(doc.id, 0) + 1 / (k + rank)
        sources[doc.id].add("vector")
        doc_map[doc.id] = doc

    # Calculate RRF scores for key results
    for rank, doc in enumerate(key_results, start=1):
        rrf_scores[doc.id] = rrf_scores.get(doc.id, 0) + 1 / (k + rank)
        sources[doc.id].add("key")
        if doc.id not in doc_map:
            doc_map[doc.id] = doc

    # Create fused documents
    fused_docs = [
        Document(
            id=doc_id,
            text=doc_map[doc_id].text,
            score=min(rrf_scores[doc_id], 1.0),  # Clamp to [0, 1]
            source="hybrid",
            metadata=doc_map[doc_id].metadata,
            vector_score=doc_map[doc_id].vector_score,
            key_score=doc_map[doc_id].key_score,
            rerank_score=None,
            retrieval_sources=list(sources[doc_id]),
        )
        for doc_id in rrf_scores
    ]

    # Sort and return top-K
    fused_docs.sort(key=lambda d: d.score, reverse=True)
    return fused_docs[:top_k]
