from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from shared.clients.tournaments_service_client import TournamentsServiceClient
from ..internal.ranking import Ranking
from ..internal.global_ranking import GlobalRanking


def tournament_rankings(request, tournament_id):
    tournament = TournamentsServiceClient.get_tournament(tournament_id)
    rankings = (
        Ranking.objects.filter(tournament=tournament_id)
        .order_by("position", "-points")
    )

    return render(
        request,
        "tournament_ranking.html",
        {"tournament": tournament, "rankings": rankings},
    )


@login_required
def my_rankings(request):
    user = request.user

    try:
        global_ranking = GlobalRanking.objects.get(player=user.id)
    except GlobalRanking.DoesNotExist:
        global_ranking = None

    tournament_rankings = (
        Ranking.objects.filter(player=user.id)
        .order_by("-tournament__start_date")
    )

    return render(
        request,
        "my_rankings.html",
        {"global_ranking": global_ranking, "tournament_rankings": tournament_rankings},
    )
