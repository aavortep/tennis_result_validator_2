from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from shared.clients.user_service_client import UserServiceClient
from apps.tournaments.internal.tournament import Tournament
from apps.tournaments.tournament_service import TournamentService


def tournament_list(request):
    tournaments = Tournament.objects.all()
    status = request.GET.get("status")
    if status:
        tournaments = tournaments.filter(status=status)

    return render(
        request, "tournament_list.html", {"tournaments": tournaments}
    )


def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.all()

    tournament_players = tournament.get_player_ids()
    all_players = UserServiceClient.get_all_players()
    available_players = []
    for player in all_players:
        if player.id not in tournament_players:
            available_players.append(player)

    tournament_referees = tournament.get_referee_ids()
    all_referees = UserServiceClient.get_all_referees()
    available_referees = []
    for referee in all_referees:
        if referee.id not in tournament_referees:
            available_referees.append(referee)

    if request.method == "POST" and request.user.is_authenticated:
        action = request.POST.get("action")
        try:
            if action == "open_registration":
                TournamentService.open_registration(tournament, request.user)
                messages.success(request, "Registration is now open!")
            elif action == "start":
                TournamentService.start_tournament(tournament, request.user)
                messages.success(request, "Tournament started!")
            elif action == "complete":
                TournamentService.complete_tournament(tournament, request.user)
                messages.success(request, "Tournament completed!")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("tournament_detail", pk=pk)

    return render(
        request,
        "tournament_detail.html",
        {
            "tournament": tournament,
            "matches": matches,
            "available_players": available_players,
            "available_referees": available_referees,
        },
    )


@login_required
def tournament_create(request):
    if request.user.role != "ORGANIZER":
        messages.error(request, "Only organizers can create tournaments.")
        return redirect("tournament_list")

    if request.method == "POST":
        try:
            data = {
                "name": request.POST.get("name"),
                "description": request.POST.get("description", ""),
                "start_date": request.POST.get("start_date"),
                "end_date": request.POST.get("end_date"),
                "location": request.POST.get("location"),
                "max_players": int(request.POST.get("max_players", 32)),
            }
            tournament = TournamentService.create_tournament(data, request.user)
            messages.success(request, "Tournament created successfully!")
            return redirect("tournament_detail", pk=tournament.id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "tournament_form.html", {"tournament": None})


@login_required
def tournament_edit(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.user != tournament.created_by:
        messages.error(request, "You can only edit your own tournaments.")
        return redirect("tournament_detail", pk=pk)

    if request.method == "POST":
        try:
            data = {
                "name": request.POST.get("name"),
                "description": request.POST.get("description", ""),
                "start_date": request.POST.get("start_date"),
                "end_date": request.POST.get("end_date"),
                "location": request.POST.get("location"),
                "max_players": int(request.POST.get("max_players", 32)),
            }
            TournamentService.update_tournament(tournament, data, request.user)
            messages.success(request, "Tournament updated!")
            return redirect("tournament_detail", pk=pk)
        except Exception as e:
            messages.error(request, str(e))

    return render(
        request, "tournament_form.html", {"tournament": tournament}
    )


@login_required
def tournament_add_player(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        player_id = request.POST.get("player_id")
        try:
            TournamentService.add_player(tournament, int(player_id), request.user)
            messages.success(request, "Player added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect("tournament_detail", pk=pk)


@login_required
def tournament_remove_player(request, pk, player_id):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        try:
            TournamentService.remove_player(tournament, player_id, request.user)
            messages.success(request, "Player removed!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect("tournament_detail", pk=pk)


@login_required
def tournament_add_referee(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        referee_id = request.POST.get("referee_id")
        try:
            TournamentService.add_referee(tournament, int(referee_id), request.user)
            messages.success(request, "Referee added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect("tournament_detail", pk=pk)
