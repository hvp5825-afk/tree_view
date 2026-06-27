from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)
    sponsor_id = serializers.CharField(required=False, allow_blank=True)
    position   = serializers.ChoiceField(choices=['LEFT', 'RIGHT'], required=False)

    class Meta:
        model  = User
        fields = ['username', 'email', 'mobile', 'password', 'password2', 'sponsor_id', 'position']

    def validate(self, data):
        if data.get('password') != data.pop('password2', None):
            raise serializers.ValidationError("Passwords do not match.")
        
        mobile = data.get('mobile', '').strip()
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            raise serializers.ValidationError({"mobile": "Mobile number must be exactly 10 digits."})
        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError({"mobile": "Mobile number already registered."})
            
        return data

    def create(self, validated_data):
        position   = validated_data.pop('position', 'LEFT')
        sponsor_id = validated_data.get('sponsor_id', '')
        plain_pwd  = validated_data['password']
        user = User.objects.create_user(**validated_data)
        user.plain_password = plain_pwd
        user.save()
        UserProfile.objects.create(user=user)
        # Create referral link if sponsor exists
        if sponsor_id:
            from network.models import Referral
            from network.utils import find_placement_parent
            try:
                sponsor = User.objects.get(member_id=sponsor_id)
                parent = find_placement_parent(sponsor, position)
                if parent is None:
                    parent = sponsor
                Referral.objects.create(sponsor=sponsor, member=user, parent=parent, position=position)
            except User.DoesNotExist:
                pass
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        exclude = ['user']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'member_id', 'sponsor_id', 'username', 'email', 'mobile', 'status', 'created_at', 'profile']
        read_only_fields = ['id', 'member_id', 'created_at']


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['member_id'] = user.member_id
        token['is_staff']  = user.is_staff
        return token


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
