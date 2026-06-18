from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.tournaments.internal.match import Match

from apps.results.internal.score import Score
from apps.results.score_service import ScoreService


@login_required
def score_submit(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if request.method == "POST":
        try:
            set_scores = []
            for i in range(1, 6):
                p1_score = request.POST.get(f"set{i}_player1")
                p2_score = request.POST.get(f"set{i}_player2")
                if p1_score and p2_score:
                    set_scores.append(
                        {"player1": int(p1_score), "player2": int(p2_score)}
                    )

            if not set_scores:
                raise ValueError("At least one set score is required")

            ScoreService.submit_score(match_id, set_scores, request.user)
            messages.success(request, "Score submitted successfully!")
            return redirect("match_detail", pk=match_id)
        except Exception as e:
            messages.error(request, str(e))

    return render(
        request,
        "results/score_form.html",
        {
            "match": match,
        },
    )


@login_required
def score_confirm(request, score_id):
    score = get_object_or_404(Score, pk=score_id)

    if request.method == "POST":
        try:
            ScoreService.confirm_score(score_id, request.user)
            messages.success(request, "Score confirmed!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect("match_detail", pk=score.match.id)
