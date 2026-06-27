import re
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, CustomTokenSerializer, ChangePasswordSerializer
from .models import UserProfile
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

User = get_user_model()


# ── Template Views ──────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')


    # Rate limiting: track failed attempts in session
    attempts = request.session.get('login_attempts', 0)
    blocked_until = request.session.get('login_blocked_until', 0)
    from django.utils import timezone
    now = timezone.now().timestamp()

    if blocked_until > now:
        remaining = int((blocked_until - now) / 60)
        messages.error(request, f'Too many login attempts. Try again in {remaining} minute(s).')
        return render(request, 'accounts/login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            request.session['login_attempts'] = 0
            request.session['login_blocked_until'] = 0
            auth_login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = 'dashboard:index'
            return redirect(next_url)
        else:
            attempts += 1
            request.session['login_attempts'] = attempts
            if attempts >= 5:
                request.session['login_blocked_until'] = now + 900  # 15 min
                messages.error(request, 'Too many login attempts. Try again in 15 minutes.')
            else:
                messages.error(request, f'Invalid credentials. {5 - attempts} attempt(s) left.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':

        pincode = request.POST.get('pincode', '').strip()
        if pincode and not re.match(r'^\d{6}$', pincode):
            messages.error(request, 'Pincode must be exactly 6 digits.')
            return redirect('accounts:edit_profile')

        account_number = request.POST.get('account_number', '').strip()
        if account_number and (not account_number.isdigit() or len(account_number) < 9):
            messages.error(request, 'Account number must be at least 9 digits.')
            return redirect('accounts:edit_profile')

        ifsc_code = request.POST.get('ifsc_code', '').strip()
        if ifsc_code and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code):
            messages.error(request, 'IFSC code must be a valid format (e.g. SBIN0001234).')
            return redirect('accounts:edit_profile')

        profile.first_name     = request.POST.get('first_name', '')
        profile.last_name      = request.POST.get('last_name', '')
        profile.address        = request.POST.get('address', '')
        profile.city           = request.POST.get('city', '')
        profile.state          = request.POST.get('state', '')
        profile.pincode        = pincode
        profile.bank_name      = request.POST.get('bank_name', '')
        profile.account_holder = request.POST.get('account_holder', '')
        profile.account_number = account_number
        profile.ifsc_code      = ifsc_code
        profile.gpay           = request.POST.get('gpay', '')
        profile.phonepe        = request.POST.get('phonepe', '')
        profile.paytm          = request.POST.get('paytm', '')
        profile.upi_id         = request.POST.get('upi_id', '')
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != request.user.email:
            try:
                validate_email(new_email)
            except ValidationError:
                messages.error(request, 'Invalid email format.')
                return redirect('accounts:edit_profile')
            if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Email already registered by another user.')
                return redirect('accounts:edit_profile')
            request.user.email = new_email

        new_mobile = request.POST.get('mobile', '').strip()
        if not new_mobile or not new_mobile.isdigit() or len(new_mobile) != 10:
            messages.error(request, 'Mobile number must be exactly 10 digits.')
            return redirect('accounts:edit_profile')
        if User.objects.filter(mobile=new_mobile).exclude(pk=request.user.pk).exists():
            messages.error(request, 'Mobile number already registered by another user.')
            return redirect('accounts:edit_profile')
        request.user.mobile = new_mobile

        request.user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/edit_profile.html', {'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_pwd  = request.POST.get('old_password', '')
        new_pwd  = request.POST.get('new_password', '')
        confirm  = request.POST.get('confirm_password', '')
        if not request.user.check_password(old_pwd):
            messages.error(request, 'Old password is incorrect.')
        elif len(new_pwd) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
        elif new_pwd != confirm:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new_pwd)
            request.user.plain_password = new_pwd
            request.user.save()
            messages.success(request, 'Password changed. Please login again.')
            return redirect('accounts:login')
    return render(request, 'accounts/change_password.html')


@login_required
def associate_list_view(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    from helpdesk.models import SendHelpRequest
    from network.models import Referral
    filter_val = request.GET.get('filter', 'all')
    qs = User.objects.filter(is_staff=False).select_related('profile')
    if filter_val == 'active':
        qs = qs.filter(status='active')
    elif filter_val == 'inactive':
        qs = qs.filter(status='inactive')
    members = []
    for i, u in enumerate(qs.order_by('-created_at'), 1):
        a_count = SendHelpRequest.objects.filter(user=u, status='accepted').count()
        p_count = SendHelpRequest.objects.filter(user=u, status='pending').count()
        r_count = SendHelpRequest.objects.filter(user=u, status='rejected').count()
        try:
            ref = u.referral_info
            parent_id = ref.parent.member_id if ref.parent else '—'
            position = ref.position
        except (Referral.DoesNotExist, AttributeError):
            parent_id = '—'
            position = '—'
        members.append({
            'sl': i, 'user': u,
            'send_a': a_count, 'send_p': p_count, 'send_r': r_count,
            'parent_id': parent_id, 'position': position,
        })
    return render(request, 'accounts/associate_list.html', {
        'members': members, 'filter_val': filter_val
    })


@login_required
def admin_add_member(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        mobile   = request.POST.get('mobile', '')
        password = request.POST.get('password')
        sponsor_id = request.POST.get('sponsor_id', '')
        position   = request.POST.get('position', 'LEFT')
        first_name = request.POST.get('first_name', '')
        last_name  = request.POST.get('last_name', '')

        if not username or not email or not password:
            messages.error(request, 'Username, Email, and Password are required.')
            return redirect('accounts:add_member')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('accounts:add_member')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('accounts:add_member')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('accounts:add_member')
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            messages.error(request, 'Mobile number must be exactly 10 digits.')
            return redirect('accounts:add_member')
        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, 'Mobile number already registered.')
            return redirect('accounts:add_member')

        user = User.objects.create_user(username=username, email=email, mobile=mobile, password=password)
        user.plain_password = password
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.save()

        # Create referral in binary tree if sponsor provided
        if sponsor_id:
            from network.models import Referral
            from network.utils import find_placement_parent
            sponsor = User.objects.filter(member_id=sponsor_id).first()
            if sponsor:
                parent = find_placement_parent(sponsor, position)
                if parent is None:
                    parent = sponsor
                Referral.objects.create(sponsor=sponsor, member=user, parent=parent, position=position)
                user.sponsor_id = sponsor.member_id
                user.save(update_fields=['sponsor_id'])
            else:
                messages.warning(request, f'Sponsor {sponsor_id} not found. Member created without sponsor.')
        messages.success(request, f'Member {user.member_id} ({username}) created successfully.')
        return redirect('accounts:associate_list')
    return render(request, 'accounts/add_member.html')


@login_required
def toggle_user_status(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        target = get_object_or_404(User, pk=pk)
        if target.is_staff:
            messages.error(request, 'Cannot toggle superadmin status.')
        else:
            target.status = 'inactive' if target.status == 'active' else 'active'
            target.save(update_fields=['status'])
            messages.success(request, f'{target.get_full_name()} is now {target.status}.')
    return redirect('accounts:associate_list')


@login_required
def remove_member(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        target = get_object_or_404(User, pk=pk)
        if target.is_staff:
            messages.error(request, 'Cannot remove superadmin.')
        else:
            target.status = 'inactive'
            target.save(update_fields=['status'])
            messages.success(request, f'{target.get_full_name()} has been removed.')
    return redirect('accounts:associate_list')


@login_required
def delete_member(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    if request.method == 'POST':
        target = get_object_or_404(User, pk=pk)
        if target.is_staff:
            messages.error(request, 'Cannot delete superadmin.')
        else:
            name = target.get_full_name()
            target.delete()
            messages.success(request, f'{name} has been permanently deleted.')
    return redirect('accounts:associate_list')


@login_required
def removed_members_list(request):
    if not request.user.is_staff:
        return redirect('dashboard:user_dashboard')
    members = User.objects.filter(status='inactive', is_staff=False).select_related('profile')
    return render(request, 'accounts/removed_members.html', {'members': members})


@login_required
def preview_id_card(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/preview_doc.html', {
        'doc_type': 'ID Card',
        'download_url': 'accounts:download_id_card',
        'fields': [
            ('Member ID', request.user.member_id),
            ('Name', request.user.get_full_name()),
            ('Mobile', request.user.mobile),
            ('Sponsor ID', request.user.sponsor_id or 'N/A'),
            ('Status', request.user.status.title()),
        ],
        'show_photo': True,
        'profile': profile,
    })


@login_required
def preview_welcome_letter(request):
    return render(request, 'accounts/preview_doc.html', {
        'doc_type': 'Welcome Letter',
        'download_url': 'accounts:download_welcome_letter',
        'is_letter': True,
        'letter_content': [
            f'Dear {request.user.get_full_name()},',
            '',
            'Welcome to TreeView MLM! We are delighted to have you on board.',
            '',
            f'Your Member ID: {request.user.member_id}',
            f'Sponsor ID: {request.user.sponsor_id or "N/A"}',
            f'Joining Date: {request.user.created_at.strftime("%d-%m-%Y")}',
            f'Status: {request.user.status.title()}',
            '',
            'We wish you great success in your journey with us.',
            '',
            'Regards,',
            'TreeView MLM Team',
        ],
    })


@login_required
def preview_joining_letter(request):
    return render(request, 'accounts/preview_doc.html', {
        'doc_type': 'Joining Letter',
        'download_url': 'accounts:download_joining_letter',
        'is_letter': True,
        'letter_content': [
            f'This is to confirm that {request.user.get_full_name()} has joined TreeView MLM.',
            '',
            f'Member ID: {request.user.member_id}',
            f'Sponsor ID: {request.user.sponsor_id or "N/A"}',
            f'Email: {request.user.email}',
            f'Mobile: {request.user.mobile}',
            f'Date of Joining: {request.user.created_at.strftime("%d-%m-%Y")}',
            f'Account Status: {request.user.status.title()}',
            '',
            'This letter serves as official confirmation of membership.',
            '',
            'Authorized Signatory',
            'TreeView MLM',
        ],
    })


@login_required
def download_id_card(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    buf = io.BytesIO()
    p = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    p.setFillColorRGB(0.1, 0.3, 0.6)
    p.roundRect(20*mm, h - 60*mm, w - 40*mm, 55*mm, 3*mm, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont('Helvetica-Bold', 18)
    p.drawCentredString(w/2, h - 30*mm, 'MEMBER ID CARD')
    p.setFont('Helvetica', 11)
    y = h - 40*mm
    p.drawString(30*mm, y, f'Member ID: {user.member_id}')
    y -= 8*mm
    p.drawString(30*mm, y, f'Name: {user.get_full_name()}')
    y -= 8*mm
    p.drawString(30*mm, y, f'Mobile: {user.mobile}')
    y -= 8*mm
    p.drawString(30*mm, y, f'Sponsor ID: {user.sponsor_id or "N/A"}')
    y -= 8*mm
    p.drawString(30*mm, y, f'Status: {user.status.title()}')
    if profile and profile.profile_image:
        try:
            img = ImageReader(profile.profile_image.path)
            p.drawImage(img, w - 50*mm, h - 55*mm, 30*mm, 30*mm, mask='auto')
        except Exception:
            pass
    p.showPage()
    p.save()
    buf.seek(0)
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename=ID_Card_{user.member_id}.pdf'
    return resp


@login_required
def download_welcome_letter(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    buf = io.BytesIO()
    p = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    p.setFont('Helvetica-Bold', 16)
    p.drawCentredString(w/2, h - 30*mm, 'WELCOME LETTER')
    p.setFont('Helvetica', 11)
    y = h - 45*mm
    lines = [
        f'Dear {user.get_full_name()},',
        '',
        f'Welcome to TreeView MLM! We are delighted to have you on board.',
        '',
        f'Your Member ID: {user.member_id}',
        f'Sponsor ID: {user.sponsor_id or "N/A"}',
        f'Joining Date: {user.created_at.strftime("%d-%m-%Y")}',
        f'Status: {user.status.title()}',
        '',
        'We wish you great success in your journey with us.',
        '',
        'Regards,',
        'TreeView MLM Team',
    ]
    for line in lines:
        p.drawString(25*mm, y, line)
        y -= 7*mm
    p.showPage()
    p.save()
    buf.seek(0)
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename=Welcome_Letter_{user.member_id}.pdf'
    return resp


@login_required
def download_joining_letter(request):
    user = request.user
    buf = io.BytesIO()
    p = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    p.setFont('Helvetica-Bold', 16)
    p.drawCentredString(w/2, h - 30*mm, 'JOINING LETTER')
    p.setFont('Helvetica', 11)
    y = h - 45*mm
    lines = [
        f'This is to confirm that {user.get_full_name()} has joined TreeView MLM.',
        '',
        f'Member ID: {user.member_id}',
        f'Sponsor ID: {user.sponsor_id or "N/A"}',
        f'Email: {user.email}',
        f'Mobile: {user.mobile}',
        f'Date of Joining: {user.created_at.strftime("%d-%m-%Y")}',
        f'Account Status: {user.status.title()}',
        '',
        'This letter serves as official confirmation of membership.',
        '',
        'Authorized Signatory',
        'TreeView MLM',
    ]
    for line in lines:
        p.drawString(25*mm, y, line)
        y -= 7*mm
    p.showPage()
    p.save()
    buf.seek(0)
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename=Joining_Letter_{user.member_id}.pdf'
    return resp


# ── API Views ────────────────────────────────────────────────────────────────

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    permission_classes = [AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data['refresh']).blacklist()
            return Response({'detail': 'Logged out.'})
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=400)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if not request.user.check_password(s.validated_data['old_password']):
            return Response({'detail': 'Wrong password.'}, status=400)
        request.user.set_password(s.validated_data['new_password'])
        request.user.plain_password = s.validated_data['new_password']
        request.user.save()
        return Response({'detail': 'Password changed.'})
