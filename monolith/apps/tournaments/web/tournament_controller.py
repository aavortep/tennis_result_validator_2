from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from shared.permissions import IsOrganizer, IsOrganizerOrReadOnly
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from apps.tournaments.internal.match import Match
from apps.tournaments.internal.tournament import Tournament
from apps.tournaments.internal.tournament_serializers import (
    AddPlayerSerializer,
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentListSerializer,
    TournamentSerializer,
)
from apps.tournaments.internal.match_serializers import MatchListSerializer
from apps.tournaments.tournament_service import TournamentService


class TournamentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TournamentCreateSerializer
        return TournamentListSerializer

    def get_queryset(self):
        queryset = Tournament.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        try:
            tournament = TournamentService.create_tournament(
                serializer.validated_data, self.request.user
            )
            serializer.instance = tournament
        except (ValidationError, PermissionDeniedError) as e:
            raise serializers.ValidationError(str(e))


class TournamentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TournamentDetailSerializer
        return TournamentSerializer

    def perform_update(self, serializer):
        try:
            TournamentService.update_tournament(
                self.get_object(), serializer.validated_data, self.request.user
            )
        except (ValidationError, PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers

            raise serializers.ValidationError(str(e))

    def perform_destroy(self, instance):
        try:
            TournamentService.delete_tournament(instance, self.request.user)
        except (PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers
            raise serializers.ValidationError(str(e))


class TournamentAddPlayerView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        serializer = AddPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.add_player(
                tournament, serializer.validated_data["player_id"], request.user
            )
            return Response({"message": "Player added successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentRemovePlayerView(APIView):
    permission_classes = [IsOrganizer]

    def delete(self, request, pk, player_id):
        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.remove_player(tournament, player_id, request.user)
            return Response({"message": "Player removed successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentAddRefereeView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        serializer = AddPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.add_referee(
                tournament, serializer.validated_data["player_id"], request.user
            )
            return Response({"message": "Referee added successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentStatusView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        action = request.data.get("action")

        try:
            tournament = Tournament.objects.get(pk=pk)

            if action == "open_registration":
                TournamentService.open_registration(tournament, request.user)
            elif action == "start":
                TournamentService.start_tournament(tournament, request.user)
            elif action == "complete":
                TournamentService.complete_tournament(tournament, request.user)
            else:
                return Response(
                    {"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "message": f"Tournament status updated to {tournament.status}.",
                    "status": tournament.status,
                }
            )
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentMatchesView(generics.ListAPIView):
    serializer_class = MatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(tournament_id=self.kwargs["pk"])
