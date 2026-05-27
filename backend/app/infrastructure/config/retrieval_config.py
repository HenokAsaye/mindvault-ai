"""Retrieval policy configuration."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.services.retrieval_policy import (
    RetrievalConfig as DomainRetrievalConfig,
)


@dataclass(slots=True, frozen=True)
class RetrievalConfig:
    """Configuration for retrieval policy and strategies."""

    top_k: int = 5
    retrieve_limit: int = 50
    fusion_weights: dict[str, float] = field(
        default_factory=lambda: {"vector": 0.6, "key": 0.4}
    )
    normalization_method: str = "softmax"
    fusion_method: str = "weighted"
    rerank_enabled: bool = False
    rerank_top_n: int = 20
    alpha: float = 0.5
    user_reranker: bool = False

    def to_domain(self) -> DomainRetrievalConfig:
        return DomainRetrievalConfig(
            top_k=self.top_k,
            retrieve_limit=self.retrieve_limit,
            fusion_weights=self.fusion_weights,
            normalization_method=self.normalization_method,
            fusion_method=self.fusion_method,
            rerank_enabled=self.rerank_enabled,
            rerank_top_n=self.rerank_top_n,
            alpha=self.alpha,
            user_reranker=self.user_reranker,
        )
