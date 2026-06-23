from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from ..internal.evidence_serializers import (
    EvidenceCreateSerializer,
    EvidenceSerializer,
)
from apps.disputes.dispute_service import DisputeService


class EvidenceCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EvidenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            evidence = DisputeService.add_evidence(
                serializer.validated_data["dispute"].id,
                serializer.validated_data.get("file"),
                serializer.validated_data["description"],
                request.user,
            )
            return Response(
                EvidenceSerializer(evidence).data, status=status.HTTP_201_CREATED
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeEvidenceView(generics.ListAPIView):
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DisputeService.get_dispute_evidence(self.kwargs["pk"])
