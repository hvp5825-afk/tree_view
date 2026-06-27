from rest_framework import serializers
from .models import SupportTicket


class SupportTicketSerializer(serializers.ModelSerializer):
    member_id   = serializers.CharField(source='user.member_id', read_only=True)
    name        = serializers.CharField(source='user.get_full_name', read_only=True)
    replied_by_name = serializers.CharField(source='replied_by.username', read_only=True, default=None)

    class Meta:
        model = SupportTicket
        fields = '__all__'
        read_only_fields = ['user', 'status', 'reply', 'replied_by', 'replied_at']
