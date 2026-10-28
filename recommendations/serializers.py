import json
from dataclasses import dataclass


@dataclass
class RecommendRequest:
    query: str
    top_k: int = 10

    MAX_TOP_K = 50


def parse_recommend_request(body: bytes) -> RecommendRequest:
    """Parse and validate the JSON body of POST /api/recommend/.

    Raises ValueError with a user-facing message on bad input.
    """
    try:
        payload = json.loads(body or b"{}")
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}") from e

    if not isinstance(payload, dict):
        raise ValueError("body must be a JSON object")

    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("'query' is required and must be a non-empty string")

    try:
        top_k = int(payload.get("top_k", 10))
    except (TypeError, ValueError) as e:
        raise ValueError("'top_k' must be an integer") from e

    if not (1 <= top_k <= RecommendRequest.MAX_TOP_K):
        raise ValueError(
            f"'top_k' must be between 1 and {RecommendRequest.MAX_TOP_K}"
        )

    return RecommendRequest(query=query.strip(), top_k=top_k)