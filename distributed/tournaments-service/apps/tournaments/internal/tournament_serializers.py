from rest_framework import serializers

from .tournament import Tournament


class TournamentSerializer(serializers.ModelSerializer):
    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "location",
            "status",
            "max_players",
            "player_count",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class TournamentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
            "location",
            "max_players",
        ]

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs


class TournamentListSerializer(serializers.ModelSerializer):
    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "location",
            "status",
            "player_count",
            "max_players",
        ]


class TournamentDetailSerializer(serializers.ModelSerializer):
    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "location",
            "status",
            "max_players",
            "player_count",
            "created_by",
            "created_at",
            "updated_at",
        ]


class AddPlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()


class AssignRefereeSerializer(serializers.Serializer):
    referee_id = serializers.IntegerField()


class AssignPlayersSerializer(serializers.Serializer):
    player1_id = serializers.IntegerField()
    player2_id = serializers.IntegerField()

    def validate(self, attrs):
        if attrs["player1_id"] == attrs["player2_id"]:
            raise serializers.ValidationError("Players must be different.")
        return attrs
