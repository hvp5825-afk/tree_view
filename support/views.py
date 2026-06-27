from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import SupportTicket
from .serializers import SupportTicketSerializer


@login_required
def ticket_create(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if not subject or not message:
            messages.error(request, 'Subject and message are required.')
            return redirect('support:create')
        ticket = SupportTicket(
            user    = request.user,
            subject = subject,
            message = message,
        )
        if 'attachment' in request.FILES:
            ticket.attachment = request.FILES['attachment']
        ticket.save()
        messages.success(request, 'Ticket submitted.')
        return redirect('support:inbox')
    return render(request, 'support/create.html')


@login_required
def inbox_view(request):
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'support/inbox.html', {'tickets': tickets})


@login_required
def admin_inbox(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    tickets = SupportTicket.objects.filter(status__in=['open', 'replied']).select_related('user')
    return render(request, 'support/admin_inbox.html', {'tickets': tickets})


@login_required
def admin_outbox(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    tickets = SupportTicket.objects.filter(status='replied').select_related('user')
    return render(request, 'support/admin_outbox.html', {'tickets': tickets})


@login_required
def admin_reply(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if request.method == 'POST':
        reply = request.POST.get('reply', '').strip()
        if not reply:
            messages.error(request, 'Reply cannot be empty.')
            return redirect('support:admin_inbox')
        ticket.reply      = reply
        ticket.status     = 'replied'
        ticket.replied_by = request.user
        ticket.replied_at = timezone.now()
        ticket.save()
        messages.success(request, 'Reply sent.')
    return redirect('support:admin_inbox')


# ── API Views ─────────────────────────────────────────────────────────────────

class TicketCreateAPIView(generics.CreateAPIView):
    serializer_class   = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketListAPIView(generics.ListAPIView):
    serializer_class   = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)


class AdminTicketListAPIView(generics.ListAPIView):
    serializer_class   = SupportTicketSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = SupportTicket.objects.select_related('user')
        s = self.request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        return qs


class AdminTicketReplyAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk)
        reply  = request.data.get('reply', '').strip()
        if not reply:
            return Response({'detail': 'Reply cannot be empty.'}, status=400)
        ticket.reply      = reply
        ticket.status     = 'replied'
        ticket.replied_by = request.user
        ticket.replied_at = timezone.now()
        ticket.save()
        return Response({'detail': 'Reply sent.'})
