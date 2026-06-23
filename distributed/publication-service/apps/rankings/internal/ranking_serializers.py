from rest_framework import serializers

from shared.clients.tournaments_service_client import TournamentsServiceClient
from shared.clients.user_service_client import UserServiceClient
from .ranking import Ranking


class RankingSerializer(serializers.ModelSerializer):
    player = serializers.IntegerField(read_only=True)
    tournament_name = serializers.SerializerMethodField()
    matches_played = serializers.ReadOnlyField()
    win_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Ranking
        fields = [
            "id",
            "player",
            "tournament",
            "tournament_name",
            "position",
            "points",
            "wins",
            "losses",
            "matches_played",
            "win_percentage",
            "sets_won",
            "sets_lost",
            "games_won",
            "games_lost",
            "created_at",
            "updated_at",
        ]
    
    def get_tournament_name(self, obj):
        tournament = TournamentsServiceClient.get_tournament(obj.tournament)
        return tournament.name


class RankingListSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    matches_played = serializers.ReadOnlyField()

    class Meta:
        model = Ranking
        fields = [
            "id",
            "player_name",
            "position",
            "points",
            "wins",
            "losses",
            "matches_played",
        ]
    
    def get_player_name(self, obj):
        player = UserServiceClient.get_user(obj.player)
        return player.username
