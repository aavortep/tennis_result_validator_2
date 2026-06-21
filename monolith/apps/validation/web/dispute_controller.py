from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import (
    CanResolveDispute,
    IsOrganizerOrReferee,
)
from shared.exceptions import (
    DisputeError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from apps.validation.internal.dispute import Dispute
from apps.validation.internal.dispute_serializers import (
    DisputeCreateSerializer,
    DisputeResolveSerializer,
    DisputeSerializer,
)
from apps.validation.dispute_service import DisputeService


class DisputeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DisputeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            dispute = DisputeService.create_dispute(
                serializer.validated_data["match"].id,
                serializer.validated_data["reason"],
                request.user,
            )
            return Response(
                DisputeSerializer(dispute).data, status=status.HTTP_201_CREATED
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            DisputeError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeListView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Dispute.objects.all()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if user.is_player:
            from django.db.models import Q

            queryset = queryset.filter(Q(match__player1=user) | Q(match__player2=user))

        elif user.is_referee:
            queryset = queryset.filter(match__referee=user)

        return queryset


class DisputeDetailView(generics.RetrieveAPIView):
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]


class DisputeResolveView(APIView):
    permission_classes = [CanResolveDispute]

    def post(self, request, pk):
        serializer = DisputeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            dispute = DisputeService.resolve_dispute(
                pk,
                serializer.validated_data["resolution_notes"],
                request.user,
                serializer.validated_data.get("final_score_id"),
                serializer.validated_data.get("winner_id"),
            )
            return Response(
                {
                    "message": "Dispute resolved successfully.",
                    "dispute": DisputeSerializer(dispute).data,
                }
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeReviewView(APIView):
    permission_classes = [CanResolveDispute]

    def post(self, request, pk):
        try:
            dispute = DisputeService.mark_under_review(pk, request.user)
            return Response(
                {
                    "message": "Dispute marked as under review.",
                    "dispute": DisputeSerializer(dispute).data,
                }
            )
        except (PermissionDeniedError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OpenDisputesView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [IsOrganizerOrReferee]

    def get_queryset(self):
        return DisputeService.get_open_disputes()
