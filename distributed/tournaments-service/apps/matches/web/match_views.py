from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.tournaments.internal.tournament import Tournament
from ..internal.match import Match
from ..match_service import MatchService
from shared.clients.user_service_client import UserServiceClient
from shared.clients.results_service_client import ResultsServiceClient


@login_required
def my_matches(request):
    user = request.user
    if user.role == "REFEREE":
        matches = Match.objects.filter(referee_id=user.id)
    elif user.role == "PLAYER":
        matches = Match.objects.filter(Q(player1_id=user.id) | Q(player2_id=user.id))
    else:
        matches = Match.objects.none()

    return render(request, "match_list.html", {"matches": matches})


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    scores = ResultsServiceClient.get_scores_by_match(match.id)
    disputes = ResultsServiceClient.get_disputes_by_match(match.id)

    if request.method == "POST" and request.user.is_authenticated:
        action = request.POST.get("action")
        if action == "start":
            try:
                MatchService.start_match(match, request.user)
                messages.success(request, "Match started!")
            except Exception as e:
                messages.error(request, str(e))
        return redirect("match_detail", pk=pk)

    return render(
        request,
        "match_detail.html",
        {
            "match": match,
            "scores": scores,
            "disputes": disputes,
        },
    )


@login_required
def match_create(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    if request.method == "POST":
        try:
            player1 = UserServiceClient.get_user(request.POST.get("player1"))
            player2 = UserServiceClient.get_user(request.POST.get("player2"))
            referee = UserServiceClient.get_user(request.POST.get("referee"))
            data = {
                "tournament": tournament,
                "player1": (
                    player1.id
                    if request.POST.get("player1")
                    else None
                ),
                "player2": (
                    player2.id
                    if request.POST.get("player2")
                    else None
                ),
                "referee": (
                    referee.id
                    if request.POST.get("referee")
                    else None
                ),
                "round": request.POST.get("round", "R32"),
                "court": request.POST.get("court", ""),
            }
            MatchService.create_match(data, request.user)
            messages.success(request, "Match created!")
            return redirect("tournament_detail", pk=tournament_id)
        except Exception as e:
            messages.error(request, str(e))

    player_ids = tournament.get_player_ids()
    referee_ids = tournament.get_referee_ids()
    players = [UserServiceClient.get_user(p_id) for p_id in player_ids]
    referees = [UserServiceClient.get_user(r_id) for r_id in referee_ids]
    return render(
        request,
        "match_form.html",
        {
            "tournament": tournament,
            "players": players,
            "referees": referees,
        },
    )


@login_required
def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)

    if request.method == "POST":
        match.court = request.POST.get("court", "")
        match.round = request.POST.get("round", match.round)
        scheduled = request.POST.get("scheduled_time")
        if scheduled:
            match.scheduled_time = scheduled
        match.save()
        messages.success(request, "Match updated!")
        return redirect("match_detail", pk=pk)

    player_ids = match.tournament.get_player_ids()
    referee_ids = match.tournament.get_referee_ids()
    players = [UserServiceClient.get_user(p_id) for p_id in player_ids]
    referees = [UserServiceClient.get_user(r_id) for r_id in referee_ids]
    return render(
        request,
        "match_form.html",
        {
            "match": match,
            "tournament": match.tournament,
            "players": players,
            "referees": referees,
        },
    )
