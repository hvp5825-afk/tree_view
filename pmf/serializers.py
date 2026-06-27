from rest_framework import serializers
from .models import PMFRequest


class PMFSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='user.member_id', read_only=True)
    name      = serializers.CharField(source='user.get_full_name', read_only=True)
    mobile    = serializers.CharField(source='user.mobile', read_only=True)

    class Meta:
        model  = PMFRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'reply_date']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be strictly positive.")
        return value

    def validate_payment_proof(self, file):
        if not file: return file
        if file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
            raise serializers.ValidationError('Only JPG, PNG, and PDF files are allowed.')
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('File size must be under 5 MB.')
        return file
