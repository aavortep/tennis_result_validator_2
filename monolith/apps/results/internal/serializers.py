from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer
from shared.utils import validate_set_scores

from .score import Score
from apps.validation.internal.dispute import Dispute
from apps.validation.internal.evidence import Evidence


class ScoreSerializer(serializers.ModelSerializer):
    submitted_by = UserPublicSerializer(read_only=True)
    confirmed_by = UserPublicSerializer(read_only=True)
    winner = UserPublicSerializer(read_only=True)
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
        return {
            "id": obj.match.id,
            "player1": obj.match.player1.username if obj.match.player1 else None,
            "player2": obj.match.player2.username if obj.match.player2 else None,
            "tournament": obj.match.tournament.name,
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
    submitted_by_name = serializers.CharField(
        source="submitted_by.username", read_only=True
    )

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
