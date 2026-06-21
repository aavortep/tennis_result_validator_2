from django.shortcuts import render

from apps.publication.internal.global_ranking import GlobalRanking


def global_rankings(request):
    rankings = GlobalRanking.objects.select_related("player").order_by(
        "position", "-total_points"
    )

    return render(request, "publication/global_ranking.html", {"rankings": rankings})
