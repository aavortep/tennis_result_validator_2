from django.shortcuts import render

from ..internal.global_ranking import GlobalRanking


def global_rankings(request):
    rankings = GlobalRanking.objects.order_by(
        "position", "-total_points"
    )

    return render(request, "global_ranking.html", {"rankings": rankings})
