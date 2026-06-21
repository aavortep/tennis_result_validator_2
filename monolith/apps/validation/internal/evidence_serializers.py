from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer

from .evidence import Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    submitted_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Evidence
        fields = ["id", "dispute", "submitted_by", "file", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class EvidenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["dispute", "file", "description"]
