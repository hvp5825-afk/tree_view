from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import ValidationError
from kyc.views import validate_file
from .models import PMFRequest
from .serializers import PMFSerializer


@login_required
def pmf_pay_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid positive amount.')
            return redirect('pmf:pay')
        prev_level = PMFRequest.objects.filter(user=request.user, status='accepted').count()
        pmf = PMFRequest(
            user           = request.user,
            amount         = amount,
            level          = prev_level + 1,
            transaction_no = request.POST.get('transaction_no', ''),
        )
        if 'payment_proof' in request.FILES:
            try:
                validate_file(request.FILES['payment_proof'])
                pmf.payment_proof = request.FILES['payment_proof']
            except ValidationError as e:
                messages.error(request, f'Payment Proof: {e.message}')
                return redirect('pmf:pay')
        pmf.save()
        messages.success(request, 'PMF payment submitted.')
        return redirect('pmf:history')
    return render(request, 'pmf/pay.html')


@login_required
def pmf_history_view(request):
    pmfs = PMFRequest.objects.filter(user=request.user)
    return render(request, 'pmf/history.html', {'pmfs': pmfs})


@login_required
def admin_pmf_list(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    status_filter = request.GET.get('status', 'pending')
    pmfs = PMFRequest.objects.filter(status=status_filter).select_related('user', 'user__profile')
    return render(request, 'pmf/admin_list.html', {'pmfs': pmfs, 'status_filter': status_filter})


@login_required
def admin_pmf_action(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    pmf = get_object_or_404(PMFRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['product_accepted', 'accepted', 'rejected', 'dispatched']:
            pmf.status     = action
            pmf.remarks    = request.POST.get('remarks', '')
            pmf.reply_date = timezone.now()
            pmf.save()
            messages.success(request, f'PMF status updated to {action}.')
        else:
            messages.error(request, 'Invalid action selected.')
    return redirect('pmf:admin_list')


class PMFCreateAPIView(generics.CreateAPIView):
    serializer_class   = PMFSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        prev_level = PMFRequest.objects.filter(user=self.request.user, status='accepted').count()
        serializer.save(user=self.request.user, level=prev_level + 1)


class PMFListAPIView(generics.ListAPIView):
    serializer_class   = PMFSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = PMFRequest.objects.select_related('user')
        s  = self.request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        return qs


class PMFActionAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        pmf    = get_object_or_404(PMFRequest, pk=pk)
        action = request.data.get('action')
        valid  = ['product_accepted', 'accepted', 'rejected', 'dispatched']
        if action not in valid:
            return Response({'detail': 'Invalid action.'}, status=400)
        pmf.status     = action
        pmf.remarks    = request.data.get('remarks', '')
        pmf.reply_date = timezone.now()
        pmf.save()
        return Response({'detail': f'PMF updated to {action}.'})
