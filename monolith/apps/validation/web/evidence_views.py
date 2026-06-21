from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from apps.validation.internal.dispute import Dispute
from apps.validation.dispute_service import DisputeService


@login_required
def evidence_add(request, dispute_id):
    dispute = get_object_or_404(Dispute, pk=dispute_id)

    if request.method == "POST":
        try:
            description = request.POST.get("description")
            file = request.FILES.get("file")

            DisputeService.add_evidence(dispute, request.user, file, description)
            messages.success(request, "Evidence added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect("dispute_detail", pk=dispute_id)
