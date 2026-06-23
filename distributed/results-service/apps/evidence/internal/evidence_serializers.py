from rest_framework import serializers

from .evidence import Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    submitted_by = serializers.IntegerField(source="evidence.submitted_by", read_only=True)

    class Meta:
        model = Evidence
        fields = ["id", "dispute", "submitted_by", "file", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class EvidenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["dispute", "file", "description"]
