from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.internal.user import User
from apps.validation.internal.dispute import Dispute
from apps.results.internal.score import Score

from apps.tournaments.internal.tournament import Tournament
from apps.tournaments.internal.match import Match
from apps.tournaments.match_service import MatchService


@login_required
def my_matches(request):
    user = request.user
    if user.role == "REFEREE":
        matches = Match.objects.filter(referee=user)
    elif user.role == "PLAYER":
        matches = Match.objects.filter(Q(player1=user) | Q(player2=user))
    else:
        matches = Match.objects.none()

    return render(request, "tournaments/match_list.html", {"matches": matches})


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    scores = Score.objects.filter(match=match)
    disputes = Dispute.objects.filter(match=match)

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
        "tournaments/match_detail.html",
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
            data = {
                "tournament": tournament,
                "player1": (
                    User.objects.get(id=request.POST.get("player1"))
                    if request.POST.get("player1")
                    else None
                ),
                "player2": (
                    User.objects.get(id=request.POST.get("player2"))
                    if request.POST.get("player2")
                    else None
                ),
                "referee": (
                    User.objects.get(id=request.POST.get("referee"))
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

    return render(
        request,
        "tournaments/match_form.html",
        {
            "tournament": tournament,
            "players": tournament.players.all(),
            "referees": tournament.referees.all(),
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

    return render(
        request,
        "tournaments/match_form.html",
        {
            "match": match,
            "tournament": match.tournament,
            "players": match.tournament.players.all(),
            "referees": match.tournament.referees.all(),
        },
    )
