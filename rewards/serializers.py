from rest_framework import serializers
from .models import Reward


class RewardSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='user.member_id', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Reward
        fields = '__all__'
        read_only_fields = ['user', 'status']
