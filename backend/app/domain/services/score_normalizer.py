import math
from typing import List


def normalize_scores_softmax(scores: List[float]) -> List[float]:
    if not scores:
        raise ValueError("Cannot normalize empty score list")

    if len(scores) == 1:
        return [1.0]

    max_score = max(scores)
    exp_scores = [math.exp(s - max_score) for s in scores]
    sum_exp = sum(exp_scores)

    return [exp_s / sum_exp for exp_s in exp_scores]


def normalize_scores_minmax(scores: List[float]) -> List[float]:
    if not scores:
        raise ValueError("Cannot normalize empty score list")

    if len(scores) == 1:
        return [1.0]

    min_score = min(scores)
    max_score = max(scores)
    range_score = max_score - min_score

    if range_score == 0:
        return [1.0 / len(scores)] * len(scores)

    return [(s - min_score) / range_score for s in scores]


def normalize_scores_zscore(scores: List[float]) -> List[float]:
    if not scores:
        raise ValueError("Cannot normalize empty score list")

    if len(scores) == 1:
        return [0.0]

    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = math.sqrt(variance)

    if std == 0:
        return [0.0] * len(scores)

    return [(s - mean) / std for s in scores]


def normalize_scores(scores: List[float], method: str = "softmax") -> List[float]:
    if method == "softmax":
        return normalize_scores_softmax(scores)
    elif method == "minmax":
        return normalize_scores_minmax(scores)
    elif method == "zscore":
        return normalize_scores_zscore(scores)
    else:
        raise ValueError(f"Unknown normalization method: {method}")
