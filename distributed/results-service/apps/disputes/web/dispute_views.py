from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from shared.clients.tournaments_service_client import TournamentsServiceClient
from apps.scores.internal.score import Score
from ..internal.dispute import Dispute
from apps.evidence.internal.evidence import Evidence
from ..dispute_service import DisputeService


@login_required
def dispute_list(request):
    user = request.user
    if user.role == "ORGANIZER":
        disputes = Dispute.objects.all()
    elif user.role == "REFEREE":
        disputes = Dispute.objects.filter(match__referee=user.id)
    else:
        disputes = Dispute.objects.filter(raised_by=user.id)

    status = request.GET.get("status")
    if status:
        disputes = disputes.filter(status=status)

    return render(request, "dispute_list.html", {"disputes": disputes})


def dispute_detail(request, pk):
    dispute = get_object_or_404(Dispute, pk=pk)
    evidence = Evidence.objects.filter(dispute=dispute)

    return render(
        request,
        "dispute_detail.html",
        {
            "dispute": dispute,
            "evidence": evidence,
        },
    )


@login_required
def dispute_create(request, match_id):
    match = TournamentsServiceClient.get_match(match_id)

    if request.method == "POST":
        try:
            reason = request.POST.get("reason")
            dispute = DisputeService.create_dispute(match, request.user, reason)
            messages.success(request, "Dispute created!")
            return redirect("dispute_detail", pk=dispute.id)
        except Exception as e:
            messages.error(request, str(e))

    return render(
        request,
        "dispute_form.html",
        {
            "match": match,
        },
    )


@login_required
def dispute_resolve(request, pk):
    dispute = get_object_or_404(Dispute, pk=pk)

    if request.method == "POST":
        try:
            resolution_notes = request.POST.get("resolution_notes")
            final_score_id = request.POST.get("final_score_id")
            final_score = (
                Score.objects.get(pk=final_score_id) if final_score_id else None
            )

            DisputeService.resolve_dispute(
                dispute, request.user, resolution_notes, final_score
            )
            messages.success(request, "Dispute resolved!")
            return redirect("dispute_detail", pk=pk)
        except Exception as e:
            messages.error(request, str(e))

    scores = Score.objects.filter(match=dispute.match)
    return render(
        request,
        "dispute_resolve.html",
        {
            "dispute": dispute,
            "scores": scores,
        },
    )
