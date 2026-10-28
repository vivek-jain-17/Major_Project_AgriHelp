from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Scheme

def scheme_list(request):
    """Public page to browse and search all schemes."""
    query = request.GET.get("q", "").strip()
    schemes = Scheme.objects.all()

    if query:
        # Search across name, description, and categories
        schemes = schemes.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ministry__icontains=query) |
            Q(department__icontains=query) |
            Q(scheme_text__icontains=query)
        ).distinct()

    # Pagination: 12 schemes per page
    paginator = Paginator(schemes, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "total_count": schemes.count(),
    }

    # If the request came from HTMX, return only the partial template
    if request.headers.get("HX-Request"):
        return render(request, "schemes/partials/scheme_grid.html", context)
    
    return render(request, "schemes/scheme_list.html", context)


def scheme_detail(request, slug):
    """Public page to view a single scheme's full details."""
    scheme = get_object_or_404(Scheme, slug=slug)
    return render(request, "schemes/scheme_detail.html", {"scheme": scheme})