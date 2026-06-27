import re
from rest_framework import serializers
from .models import KYCRequest


class KYCSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='user.member_id', read_only=True)
    name      = serializers.CharField(source='user.get_full_name', read_only=True)
    mobile    = serializers.CharField(source='user.mobile', read_only=True)

    class Meta:
        model  = KYCRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'reviewed_at']

    def validate_aadhaar_number(self, value):
        if not re.match(r'^\d{12}$', value):
            raise serializers.ValidationError('Aadhaar number must be exactly 12 digits.')
        return value

    def validate_pan_number(self, value):
        if not re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', value):
            raise serializers.ValidationError('PAN number must be a valid 10-character PAN (e.g. ABCDE1234F).')
        return value

    def _validate_file(self, file):
        if not file: return file
        if file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
            raise serializers.ValidationError('Only JPG, PNG, and PDF files are allowed.')
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('File size must be under 5 MB.')
        return file

    def validate_aadhaar_file(self, value): return self._validate_file(value)
    def validate_pan_file(self, value): return self._validate_file(value)
    def validate_bank_file(self, value): return self._validate_file(value)
    def validate_photo_file(self, value): return self._validate_file(value)
