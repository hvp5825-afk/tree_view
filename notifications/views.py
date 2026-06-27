from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Notification, QRCode
from .serializers import NotificationSerializer, QRCodeSerializer

User = get_user_model()


@login_required
def add_notification(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        notif_type = request.POST.get('notif_type', 'global')
        message = request.POST.get('message', '').strip()
        if not message:
            messages.error(request, 'Notification message cannot be empty.')
            return redirect('notifications:add')
        member_id = request.POST.get('member_id', '')
        user = None
        if notif_type == 'individual':
            if not member_id:
                messages.error(request, 'Member ID is required for individual notification.')
                return redirect('notifications:add')
            try:
                user = User.objects.get(member_id=member_id)
            except User.DoesNotExist:
                messages.error(request, f'Member {member_id} not found.')
                return redirect('notifications:add')
        Notification.objects.create(user=user, notif_type=notif_type, message=message)
        messages.success(request, 'Notification sent.')
        return redirect('notifications:add')
    notifs = Notification.objects.select_related('user').order_by('-created_at')
    return render(request, 'notifications/add.html', {'notifs': notifs})


@login_required
def delete_notification(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        get_object_or_404(Notification, pk=pk).delete()
        messages.success(request, 'Notification deleted.')
    return redirect('notifications:add')


@login_required
def add_qrcode(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'Title is required.')
            return redirect('notifications:qrcode')
        QRCode.objects.create(
            title=title,
            bank_name=request.POST.get('bank_name', ''),
            account_no=request.POST.get('account_no', ''),
            ifsc_code=request.POST.get('ifsc_code', ''),
            account_holder=request.POST.get('account_holder', ''),
            qr_type=request.POST.get('qr_type', 'bank'),
            qr_image=request.FILES.get('qr_image'),
        )
        messages.success(request, 'QR Code added.')
        return redirect('notifications:qrcode')
    qrcodes = QRCode.objects.all()
    return render(request, 'notifications/qrcode.html', {'qrcodes': qrcodes})


@login_required
def delete_qrcode(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        get_object_or_404(QRCode, pk=pk).delete()
        messages.success(request, 'QR Code deleted.')
    return redirect('notifications:qrcode')


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user) | Notification.objects.filter(notif_type='global')


class QRCodeListAPIView(generics.ListAPIView):
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QRCode.objects.all()
