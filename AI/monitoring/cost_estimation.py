"""
Cost estimation (Sprint MVP)

Purpose:
- Provide rough (order-of-magnitude) cost estimates per request.
- No provider-specific billing accuracy.
- Uses approximate token counts derived from word count.

Notes:
- Adjust PRICING_* constants later when the team selects a model/provider.
"""

from dataclasses import dataclass
from typing import Optional


# -----------------------------
# Simple pricing configuration
# -----------------------------
# Placeholder pricing per 1K tokens (USD).
# Replace with your chosen provider/model values later.
DEFAULT_INPUT_COST_PER_1K = 0.0020
DEFAULT_OUTPUT_COST_PER_1K = 0.0020

# Rough heuristic: tokens ≈ words * 1.3 (English technical text tends to be close).
WORDS_TO_TOKENS = 1.3


@dataclass
class CostEstimate:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    model_name: str


def estimate_tokens_from_text(text: str) -> int:
    words = len(text.split())
    return int(words * WORDS_TO_TOKENS)


def estimate_cost(
    input_tokens: int,
    output_tokens: int = 0,
    input_cost_per_1k: float = DEFAULT_INPUT_COST_PER_1K,
    output_cost_per_1k: float = DEFAULT_OUTPUT_COST_PER_1K,
    model_name: str = "placeholder-model",
) -> CostEstimate:
    total_tokens = input_tokens + output_tokens
    cost = (input_tokens / 1000.0) * input_cost_per_1k + (output_tokens / 1000.0) * output_cost_per_1k
    return CostEstimate(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=round(cost, 6),
        model_name=model_name,
    )


def estimate_cost_from_text(
    text: str,
    expected_output_tokens: int = 0,
    input_cost_per_1k: float = DEFAULT_INPUT_COST_PER_1K,
    output_cost_per_1k: float = DEFAULT_OUTPUT_COST_PER_1K,
    model_name: str = "placeholder-model",
) -> CostEstimate:
    in_tokens = estimate_tokens_from_text(text)
    return estimate_cost(
        input_tokens=in_tokens,
        output_tokens=expected_output_tokens,
        input_cost_per_1k=input_cost_per_1k,
        output_cost_per_1k=output_cost_per_1k,
        model_name=model_name,
    )
