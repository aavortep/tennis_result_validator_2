from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.tournaments.internal.tournament import Tournament
from apps.publication.internal.ranking import Ranking
from apps.publication.internal.global_ranking import GlobalRanking


def tournament_rankings(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    rankings = (
        Ranking.objects.filter(tournament=tournament)
        .select_related("player")
        .order_by("position", "-points")
    )

    return render(
        request,
        "publication/tournament_ranking.html",
        {"tournament": tournament, "rankings": rankings},
    )


@login_required
def my_rankings(request):
    user = request.user

    try:
        global_ranking = GlobalRanking.objects.get(player=user)
    except GlobalRanking.DoesNotExist:
        global_ranking = None

    tournament_rankings = (
        Ranking.objects.filter(player=user)
        .select_related("tournament")
        .order_by("-tournament__start_date")
    )

    return render(
        request,
        "publication/my_rankings.html",
        {"global_ranking": global_ranking, "tournament_rankings": tournament_rankings},
    )
