from rest_framework import serializers

from shared.clients.user_service_client import UserServiceClient
from shared.clients.tournaments_service_client import TournamentsServiceClient
from shared.utils import validate_set_scores

from .score import Score


class ScoreSerializer(serializers.ModelSerializer):
    submitted_by = serializers.IntegerField(source="score.submitted_by", read_only=True)
    confirmed_by = serializers.IntegerField(source="score.confirmed_by", read_only=True)
    winner = serializers.IntegerField(source="score.winner", read_only=True)
    match_info = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = [
            "id",
            "match",
            "match_info",
            "submitted_by",
            "set_scores",
            "winner",
            "is_confirmed",
            "confirmed_by",
            "confirmed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_match_info(self, obj):
        match = TournamentsServiceClient.get_match(obj.match)
        player1 = UserServiceClient.get_user(match.player1) if match.player1 else None
        player2 = UserServiceClient.get_user(match.player2) if match.player2 else None
        return {
            "id": obj.match,
            "player1": player1.username if player1 else None,
            "player2": player2.username if player2 else None,
            "tournament": match.tournament.name,
        }


class ScoreSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ["match", "set_scores"]

    def validate_set_scores(self, value):
        is_valid, error = validate_set_scores(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value


class ScoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ["set_scores"]

    def validate_set_scores(self, value):
        is_valid, error = validate_set_scores(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value


class ScoreListSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = [
            "id",
            "match",
            "submitted_by_name",
            "set_scores",
            "is_confirmed",
            "created_at",
        ]
    
    def get_submitted_by_name(self, obj):
        submitted_by_user = UserServiceClient.get_user(obj.submitted_by)
        return submitted_by_user.username
