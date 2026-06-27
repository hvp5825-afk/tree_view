from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import ValidationError
from kyc.views import validate_file
from .models import SendHelpRequest, ReceiveHelpRequest
from .serializers import SendHelpSerializer, ReceiveHelpSerializer

User = get_user_model()


@login_required
def send_help_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid positive amount.')
            return redirect('helpdesk:send')

        request_to_id = request.POST.get('request_to', '').strip()
        if not request_to_id:
            messages.error(request, 'Please enter a recipient Member ID.')
            return redirect('helpdesk:send')

        if request_to_id == request.user.member_id:
            messages.error(request, 'You cannot send help to yourself.')
            return redirect('helpdesk:send')

        try:
            recipient = User.objects.get(member_id=request_to_id)
        except User.DoesNotExist:
            messages.error(request, f'Member {request_to_id} not found.')
            return redirect('helpdesk:send')

        sh = SendHelpRequest(
            user           = request.user,
            request_to     = recipient,
            amount         = amount,
            payment_method = request.POST.get('payment_method'),
            transaction_no = request.POST.get('transaction_no', ''),
            remarks        = request.POST.get('remarks', ''),
        )
        if 'proof_file' in request.FILES:
            try:
                validate_file(request.FILES['proof_file'])
                sh.proof_file = request.FILES['proof_file']
            except ValidationError as e:
                messages.error(request, f'Proof File: {e.message}')
                return redirect('helpdesk:send')
        sh.save()
        messages.success(request, 'Send Help request submitted.')
        return redirect('helpdesk:send_history')
    return render(request, 'helpdesk/send_help.html')


@login_required
def send_help_history(request):
    reqs = SendHelpRequest.objects.filter(user=request.user)
    return render(request, 'helpdesk/send_history.html', {'requests': reqs})


@login_required
def receive_help_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid positive amount.')
            return redirect('helpdesk:receive')
        ReceiveHelpRequest.objects.create(
            user   = request.user,
            amount = amount,
        )
        messages.success(request, 'Receive Help request submitted.')
        return redirect('helpdesk:receive_history')
    return render(request, 'helpdesk/receive_help.html')


@login_required
def receive_help_history(request):
    reqs = ReceiveHelpRequest.objects.filter(user=request.user)
    return render(request, 'helpdesk/receive_history.html', {'requests': reqs})


@login_required
def admin_help_list(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    status_filter = request.GET.get('status', 'pending')
    sends = SendHelpRequest.objects.filter(status=status_filter).select_related('user', 'request_to')
    return render(request, 'helpdesk/admin_list.html', {'sends': sends, 'status_filter': status_filter})


@login_required
def admin_help_action(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    if request.method == 'POST':
        sh     = get_object_or_404(SendHelpRequest, pk=pk)
        action = request.POST.get('action')
        if action in ['accepted', 'rejected']:
            sh.status  = action
            sh.remarks = request.POST.get('remarks', sh.remarks)
            sh.save()
            messages.success(request, f'Help request {action}.')
        else:
            messages.error(request, 'Invalid action selected.')
    return redirect('helpdesk:admin_list')


# ── API Views ─────────────────────────────────────────────────────────────────

class SendHelpCreateAPIView(generics.CreateAPIView):
    serializer_class   = SendHelpSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SendHelpListAPIView(generics.ListAPIView):
    serializer_class   = SendHelpSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = SendHelpRequest.objects.all()
        s  = self.request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        return qs


class ReceiveHelpCreateAPIView(generics.CreateAPIView):
    serializer_class   = ReceiveHelpSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminHelpActionAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        sh     = get_object_or_404(SendHelpRequest, pk=pk)
        action = request.data.get('action')
        if action not in ['accepted', 'rejected']:
            return Response({'detail': 'Invalid action.'}, status=400)
        sh.status  = action
        sh.remarks = request.data.get('remarks', sh.remarks)
        sh.save()
        return Response({'detail': f'Help request {action}.'})
