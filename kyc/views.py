import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import KYCRequest
from .serializers import KYCSerializer
from notifications.models import Notification


# ── Template Views ────────────────────────────────────────────────────────────

ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_file(file):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise ValidationError('Only JPG, PNG, and PDF files are allowed.')
    if file.size > MAX_FILE_SIZE:
        raise ValidationError('File size must be under 5 MB.')


@login_required
def kyc_submit_view(request):
    kyc = KYCRequest.objects.filter(user=request.user).first()
    if request.method == 'POST' and (not kyc or kyc.status == 'rejected'):
        aadhaar = request.POST.get('aadhaar_number', '').strip()
        pan     = request.POST.get('pan_number', '').strip()

        if not re.match(r'^\d{12}$', aadhaar):
            messages.error(request, 'Aadhaar number must be exactly 12 digits.')
            return redirect('kyc:submit')
        if not re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', pan):
            messages.error(request, 'PAN number must be a valid 10-character PAN (e.g. ABCDE1234F).')
            return redirect('kyc:submit')

        kyc, _ = KYCRequest.objects.get_or_create(user=request.user)
        kyc.aadhaar_number = aadhaar
        kyc.pan_number     = pan

        for field in ['aadhaar_file', 'pan_file', 'bank_file', 'photo_file']:
            if field in request.FILES:
                try:
                    validate_file(request.FILES[field])
                    setattr(kyc, field, request.FILES[field])
                except ValidationError as e:
                    messages.error(request, f'{field.replace("_"," ").title()}: {e.message}')
                    return redirect('kyc:submit')

        kyc.status = 'pending'
        kyc.remarks = ''
        kyc.save()
        messages.success(request, 'KYC submitted successfully.')
        return redirect('kyc:status')
    return render(request, 'kyc/submit.html', {'kyc': kyc})


@login_required
def kyc_status_view(request):
    kyc = KYCRequest.objects.filter(user=request.user).first()
    return render(request, 'kyc/status.html', {'kyc': kyc})


@login_required
def admin_kyc_list(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    status_filter = request.GET.get('status', 'pending')
    kycs = KYCRequest.objects.filter(status=status_filter).select_related('user', 'user__profile')
    return render(request, 'kyc/admin_list.html', {'kycs': kycs, 'status_filter': status_filter})


@login_required
def admin_kyc_action(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    kyc = get_object_or_404(KYCRequest, pk=pk)
    if request.method == 'POST':
        action  = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        if action in ['accepted', 'rejected']:
            kyc.status      = action
            kyc.remarks     = remarks
            kyc.reviewed_at = timezone.now()
            kyc.save()
            if action == 'accepted':
                kyc.user.status = 'active'
                kyc.user.save()
                Notification.objects.create(
                    user=kyc.user, notif_type='individual',
                    message='Your KYC has been accepted. You are now an active member.'
                )
            else:
                Notification.objects.create(
                    user=kyc.user, notif_type='individual',
                    message=f'Your KYC has been rejected: {remarks}. Please apply for re-KYC.'
                )
            messages.success(request, f'KYC {action}.')
        else:
            messages.error(request, 'Invalid action selected.')
    return redirect('kyc:admin_list')


# ── API Views ─────────────────────────────────────────────────────────────────

class KYCSubmitAPIView(generics.CreateAPIView):
    serializer_class   = KYCSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class KYCListAPIView(generics.ListAPIView):
    serializer_class   = KYCSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = KYCRequest.objects.select_related('user')
        s  = self.request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        return qs


class KYCActionAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        kyc    = get_object_or_404(KYCRequest, pk=pk)
        action = request.data.get('action')
        if action not in ['accepted', 'rejected']:
            return Response({'detail': 'Invalid action.'}, status=400)
        kyc.status      = action
        kyc.remarks     = request.data.get('remarks', '')
        kyc.reviewed_at = timezone.now()
        kyc.save()
        if action == 'accepted':
            kyc.user.status = 'active'
            kyc.user.save()
        return Response({'detail': f'KYC {action}.'})
