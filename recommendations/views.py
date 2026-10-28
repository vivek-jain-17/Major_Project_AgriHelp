from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from recommender.engine import HybridRecommender

from .serializers import parse_recommend_request


@csrf_exempt
@require_POST
def recommend(request):
    try:
        req = parse_recommend_request(request.body)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    engine = HybridRecommender.get()
    results = engine.recommend(req.query, top_k=req.top_k)

    return JsonResponse(
        {
            "query": req.query,
            "top_k": req.top_k,
            "count": len(results),
            "results": results,
        }
    )