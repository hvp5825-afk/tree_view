from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from helpdesk.models import SendHelpRequest, ReceiveHelpRequest
from pmf.models import PMFRequest
from rewards.models import Reward
from notifications.models import Notification

User = get_user_model()


@login_required
def index(request):
    if request.user.is_staff:
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:user_dashboard')


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    ctx = {
        'total_members':    User.objects.filter(is_staff=False).count(),
        'active_members':   User.objects.filter(is_staff=False, status='active').count(),
        'inactive_members': User.objects.filter(is_staff=False, status='inactive').count(),
        'total_help':       SendHelpRequest.objects.filter(status='accepted').aggregate(t=Sum('amount'))['t'] or 0,
        'pending_help':     SendHelpRequest.objects.filter(status='pending').count(),
        'accepted_help':    SendHelpRequest.objects.filter(status='accepted').count(),
        'rejected_help':    SendHelpRequest.objects.filter(status='rejected').count(),
        'pending_pmf':      PMFRequest.objects.filter(status='pending').count(),
        'notifications':    Notification.objects.filter(notif_type='global').order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', ctx)


@login_required
def user_dashboard(request):
    user = request.user
    from network.models import Referral
    try:
        ref = Referral.objects.get(member=user)
        sponsor = ref.sponsor
    except Referral.DoesNotExist:
        sponsor = None

    directs = Referral.objects.filter(sponsor=user).select_related('member')
    send_count    = user.send_help_requests.count()
    receive_count = user.receive_help_requests.count()
    notifications = Notification.objects.filter(
        notif_type='global'
    ).order_by('-created_at')[:5]

    ctx = {
        'sponsor': sponsor,
        'directs_count': directs.count(),
        'send_count':    send_count,
        'receive_count': receive_count,
        'notifications': notifications,
    }
    return render(request, 'dashboard/user_dashboard.html', ctx)
