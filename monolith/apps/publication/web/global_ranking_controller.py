from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.publication.internal.global_ranking import GlobalRanking
from apps.publication.internal.global_ranking_serializers import (
    GlobalRankingListSerializer,
    GlobalRankingSerializer,
)
from apps.publication.ranking_service import RankingService


class GlobalLeaderboardView(generics.ListAPIView):
    serializer_class = GlobalRankingListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RankingService.get_global_leaderboard()


class MyGlobalRankingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            ranking = GlobalRanking.objects.get(player=request.user)
            return Response(GlobalRankingSerializer(ranking).data)
        except GlobalRanking.DoesNotExist:
            return Response({"message": "No global ranking found.", "ranking": None})
