from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Reward
from .serializers import RewardSerializer


@login_required
def rewards_view(request):
    rewards = Reward.objects.filter(user=request.user)
    return render(request, 'rewards/list.html', {'rewards': rewards})


@login_required
def admin_rewards_list(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    status_filter = request.GET.get('status', 'pending')
    rewards = Reward.objects.filter(status=status_filter).select_related('user')
    return render(request, 'rewards/admin_list.html', {'rewards': rewards, 'status_filter': status_filter})


@login_required
def admin_reward_action(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        reward = get_object_or_404(Reward, pk=pk)
        action = request.POST.get('action')
        if action in ['accepted', 'rejected']:
            reward.status = action
            reward.remarks = request.POST.get('remarks', '')
            reward.save()
            messages.success(request, f'Reward {action}.')
        else:
            messages.error(request, 'Invalid action selected.')
    return redirect('rewards:admin_list')


class RewardListAPIView(generics.ListAPIView):
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reward.objects.filter(user=self.request.user)


class AdminRewardListAPIView(generics.ListAPIView):
    serializer_class = RewardSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Reward.objects.select_related('user')
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)
        return qs
