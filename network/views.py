from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Referral

User = get_user_model()


def build_tree(user, depth=4):
    """Recursively build binary tree dict up to given depth."""
    if depth == 0 or user is None:
        return None
    node = {
        'member_id': user.member_id,
        'name': user.get_full_name(),
        'status': user.status,
        'left': None,
        'right': None,
    }
    left_ref  = Referral.objects.filter(parent=user, position='LEFT').select_related('member').first()
    right_ref = Referral.objects.filter(parent=user, position='RIGHT').select_related('member').first()
    if left_ref:
        node['left']  = build_tree(left_ref.member, depth - 1)
    if right_ref:
        node['right'] = build_tree(right_ref.member, depth - 1)
    return node


@login_required
def tree_view(request):
    member_id = request.GET.get('member_id', request.user.member_id)
    # Non-staff can only view their own tree
    if not request.user.is_staff and member_id != request.user.member_id:
        member_id = request.user.member_id
    try:
        root_user = User.objects.get(member_id=member_id)
    except User.DoesNotExist:
        root_user = request.user
    tree = build_tree(root_user)
    return render(request, 'network/tree.html', {'tree': tree, 'root_member_id': root_user.member_id})


@login_required
def referrals_view(request):
    directs = Referral.objects.filter(sponsor=request.user).select_related('member', 'member__profile')
    left_team  = Referral.objects.filter(parent=request.user, position='LEFT').select_related('member')
    right_team = Referral.objects.filter(parent=request.user, position='RIGHT').select_related('member')
    ctx = {
        'directs':    directs,
        'left_total': left_team.count(),
        'left_active': left_team.filter(member__status='active').count(),
        'right_total': right_team.count(),
        'right_active': right_team.filter(member__status='active').count(),
    }
    return render(request, 'network/referrals.html', ctx)


class TreeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member_id = request.query_params.get('member_id', request.user.member_id)
        if not request.user.is_staff and member_id != request.user.member_id:
            return Response({'error': 'Forbidden'}, status=403)
        try:
            root_user = User.objects.get(member_id=member_id)
        except User.DoesNotExist:
            return Response({'error': 'Member not found'}, status=404)
        return Response(build_tree(root_user))
