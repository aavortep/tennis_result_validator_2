from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsOrganizer, IsOrganizerOrReadOnly
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from ..internal.match import Match
from apps.tournaments.internal.tournament_serializers import (
    AssignPlayersSerializer,
    AssignRefereeSerializer,
)
from ..internal.match_serializers import (
    MatchCreateSerializer,
    MatchListSerializer,
    MatchSerializer,
)
from ..match_service import MatchService


class MatchListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MatchCreateSerializer
        return MatchListSerializer

    def get_queryset(self):
        queryset = Match.objects.all()
        tournament_id = self.request.query_params.get("tournament")
        status_filter = self.request.query_params.get("status")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        try:
            match = MatchService.create_match(
                serializer.validated_data, self.request.user
            )
            serializer.instance = match
        except (ValidationError, PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers
            raise serializers.ValidationError(str(e))


class MatchDetailView(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]


class MyMatchesView(generics.ListAPIView):
    serializer_class = MatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_referee:
            return Match.objects.filter(referee_id=user.id)
        elif user.is_player:
            return Match.objects.filter(Q(player1_id=user.id) | Q(player2_id=user.id))
        return Match.objects.none()


class MatchAssignPlayersView(APIView):
    permission_classes = [IsOrganizer]

    def put(self, request, pk):
        serializer = AssignPlayersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            match = Match.objects.get(pk=pk)
            MatchService.assign_players(
                match,
                serializer.validated_data["player1_id"],
                serializer.validated_data["player2_id"],
                request.user,
            )
            return Response(MatchSerializer(match).data)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchAssignRefereeView(APIView):
    permission_classes = [IsOrganizer]

    def put(self, request, pk):
        serializer = AssignRefereeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            match = Match.objects.get(pk=pk)
            MatchService.assign_referee(
                match, serializer.validated_data["referee_id"], request.user
            )
            return Response(MatchSerializer(match).data)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (NotFoundError, PermissionDeniedError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            match = Match.objects.get(pk=pk)
            MatchService.start_match(match, request.user)
            return Response({"message": "Match started.", "status": match.status})
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
