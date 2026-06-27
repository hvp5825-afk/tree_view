from rest_framework import serializers
from .models import Notification, QRCode


class NotificationSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='user.member_id', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['is_read', 'created_at']


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'
