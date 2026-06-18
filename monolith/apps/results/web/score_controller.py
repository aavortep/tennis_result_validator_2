from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import CanSubmitScore
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from apps.results.internal.score import Score
from apps.results.internal.serializers import (
    ScoreListSerializer,
    ScoreSerializer,
    ScoreSubmitSerializer,
    ScoreUpdateSerializer,
)
from apps.results.score_service import ScoreService


class ScoreSubmitView(APIView):
    permission_classes = [CanSubmitScore]

    def post(self, request):
        serializer = ScoreSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.submit_score(
                serializer.validated_data["match"].id,
                serializer.validated_data["set_scores"],
                request.user,
            )
            return Response(ScoreSerializer(score).data, status=status.HTTP_201_CREATED)
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Score.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ScoreUpdateSerializer
        return ScoreSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.update_score(
                self.kwargs["pk"], serializer.validated_data["set_scores"], request.user
            )
            return Response(ScoreSerializer(score).data)
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            ScoreService.delete_score(self.kwargs["pk"], request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreConfirmView(APIView):
    permission_classes = [CanSubmitScore]

    def post(self, request, pk):
        try:
            score = ScoreService.confirm_score(pk, request.user)
            return Response(
                {
                    "message": "Score confirmed successfully.",
                    "score": ScoreSerializer(score).data,
                }
            )
        except (ValidationError, PermissionDeniedError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchScoresView(generics.ListAPIView):
    serializer_class = ScoreListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScoreService.get_match_scores(self.kwargs["match_id"])
