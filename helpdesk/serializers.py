from rest_framework import serializers
from .models import SendHelpRequest, ReceiveHelpRequest


class SendHelpSerializer(serializers.ModelSerializer):
    request_to_id   = serializers.CharField(source='request_to.member_id', read_only=True)
    request_by_id   = serializers.CharField(source='user.member_id', read_only=True)

    class Meta:
        model  = SendHelpRequest
        fields = '__all__'
        read_only_fields = ['user', 'status']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be strictly positive.")
        return value

    def validate_proof_file(self, file):
        if not file: return file
        if file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
            raise serializers.ValidationError('Only JPG, PNG, and PDF files are allowed.')
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('File size must be under 5 MB.')
        return file

class ReceiveHelpSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='user.member_id', read_only=True)

    class Meta:
        model  = ReceiveHelpRequest
        fields = '__all__'
        read_only_fields = ['user', 'status']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be strictly positive.")
        return value
