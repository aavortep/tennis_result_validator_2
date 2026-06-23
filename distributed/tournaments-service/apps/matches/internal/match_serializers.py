from rest_framework import serializers

from .match import Match


class MatchSerializer(serializers.ModelSerializer):
    player1_id = serializers.IntegerField(source="match.player1_id", read_only=True)
    player2_id = serializers.IntegerField(source="match.player2_id", read_only=True)
    referee_id = serializers.IntegerField(source="match.referee_id", read_only=True)
    winner_id = serializers.IntegerField(source="match.winner_id", read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament",
            "tournament_name",
            "player1_id",
            "player2_id",
            "referee_id",
            "scheduled_time",
            "court",
            "round",
            "status",
            "winner_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            "tournament",
            "player1_id",
            "player2_id",
            "referee_id",
            "scheduled_time",
            "court",
            "round",
        ]


class MatchListSerializer(serializers.ModelSerializer):
    player1_id = serializers.IntegerField(source="match.player1_id", read_only=True)
    player2_id = serializers.IntegerField(source="match.player2_id", read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament_name",
            "player1_id",
            "player2_id",
            "scheduled_time",
            "court",
            "round",
            "status",
        ]
