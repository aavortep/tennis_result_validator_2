from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer

from .dispute import Dispute


class DisputeSerializer(serializers.ModelSerializer):
    raised_by = UserPublicSerializer(read_only=True)
    resolved_by = UserPublicSerializer(read_only=True)
    evidence_count = serializers.SerializerMethodField()

    class Meta:
        model = Dispute
        fields = [
            "id",
            "match",
            "raised_by",
            "reason",
            "status",
            "resolved_by",
            "resolution_notes",
            "resolved_at",
            "evidence_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_evidence_count(self, obj):
        return obj.evidence.count()


class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ["match", "reason"]


class DisputeResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=True)
    final_score_id = serializers.IntegerField(required=False, allow_null=True)
    winner_id = serializers.IntegerField(required=False, allow_null=True)
