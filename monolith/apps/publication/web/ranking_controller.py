from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsOrganizer

from apps.users.internal.user import User
from apps.publication.internal.ranking import Ranking
from apps.publication.internal.ranking_serializers import (
    RankingListSerializer,
    RankingSerializer,
)
from apps.publication.ranking_service import RankingService


class TournamentLeaderboardView(generics.ListAPIView):
    serializer_class = RankingListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RankingService.get_tournament_leaderboard(self.kwargs["tournament_id"])


class PlayerRankingsView(generics.ListAPIView):
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        player_id = self.kwargs.get("player_id", self.request.user.id)
        return RankingService.get_player_rankings(player_id)


class MyRankingsView(generics.ListAPIView):
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RankingService.get_player_rankings(self.request.user.id)


class RankingDetailView(generics.RetrieveAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]


class InitializeTournamentRankingsView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, tournament_id):
        from apps.tournaments.models import Tournament

        try:
            tournament = Tournament.objects.get(id=tournament_id)
            RankingService.initialize_tournament_rankings(tournament)
            return Response(
                {
                    "message": "Tournament rankings initialized.",
                    "player_count": tournament.players.count(),
                }
            )
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found."}, status=404)


class RecalculateRankingsView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, tournament_id):
        from apps.tournaments.models import Tournament

        try:
            tournament = Tournament.objects.get(id=tournament_id)
            RankingService.recalculate_positions(tournament)
            return Response({"message": "Rankings recalculated."})
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found."}, status=404)


class HeadToHeadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, player1_id, player2_id):
        if not User.objects.filter(id=player1_id).exists():
            return Response({"error": "Player 1 not found."}, status=404)
        if not User.objects.filter(id=player2_id).exists():
            return Response({"error": "Player 2 not found."}, status=404)

        stats = RankingService.get_head_to_head(player1_id, player2_id)
        return Response(stats)
