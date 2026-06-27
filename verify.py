import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treeview_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.conf import settings
from products.models import Product
from rest_framework.test import APIRequestFactory, force_authenticate
import os.path

User = get_user_model()
factory = RequestFactory()
rf = APIRequestFactory()

def make(method='GET', path='/', data=None, user=None):
    r = factory.post(path, data or {}) if method == 'POST' else factory.get(path, data or {})
    r.user = user
    SessionMiddleware(lambda x: None).process_request(r)
    r.session.save()
    MessageMiddleware(lambda x: None).process_request(r)
    return r

passed = 0
failed = 0

def test(name, func, method='GET', data=None, user=None, expect=200, path_args=None, path_kwargs=None):
    global passed, failed
    try:
        r = make(method, '/', data, user)
        if path_args or path_kwargs:
            resp = func(r, *(path_args or []), **(path_kwargs or {}))
        else:
            resp = func(r)
        s = resp.status_code
        ok = s == expect
        if ok: passed += 1
        else: failed += 1
        print(f'  [{"PASS" if ok else "FAIL"}] {name} ({s})' + ('' if ok else f' expected {expect}'))
    except Exception as e:
        failed += 1
        import traceback
        print(f'  [FAIL] {name}: {e}')
        traceback.print_exc()
    return ok

admin = User.objects.filter(is_superuser=True).first()
member = User.objects.filter(is_staff=False, is_superuser=False).first()
print(f'Admin: {admin.member_id}  Member: {member.member_id}')

# ── ADMIN TEMPLATE VIEWS ──
print('\n--- Admin Template Views ---')
from dashboard.views import admin_dashboard
test('Admin Dashboard', admin_dashboard, user=admin)
test('Admin Dashboard (member redirect)', admin_dashboard, user=member, expect=302)

from accounts.views import associate_list_view
test('Associate List', associate_list_view, user=admin)
test('Associate List (member redirect)', associate_list_view, user=member, expect=302)

# KYC
from kyc.views import admin_kyc_list, admin_kyc_action
test('KYC Admin List', admin_kyc_list, user=admin)
kyc_rec = User.objects.filter(kyc__isnull=False).first()
if kyc_rec and kyc_rec.kyc:
    test('KYC Accept Action', admin_kyc_action, 'POST',
         {'action':'accepted','remarks':'OK'}, admin, expect=302, path_args=[kyc_rec.kyc.pk])

# PMF
from pmf.views import admin_pmf_list, admin_pmf_action
test('PMF Admin List', admin_pmf_list, user=admin)
pmf_rec = User.objects.filter(pmf_requests__isnull=False).first()
if pmf_rec:
    p = pmf_rec.pmf_requests.first()
    if p:
        test('PMF Accept Action', admin_pmf_action, 'POST',
             {'action':'accepted','remarks':'OK'}, admin, expect=302, path_args=[p.pk])

# Help
from helpdesk.views import admin_help_list, admin_help_action
test('Help Admin List', admin_help_list, user=admin)
sh_rec = User.objects.filter(send_help_requests__isnull=False).first()
if sh_rec:
    sh = sh_rec.send_help_requests.first()
    if sh:
        test('Help Accept Action', admin_help_action, 'POST',
             {'action':'accepted','remarks':'OK'}, admin, expect=302, path_args=[sh.pk])

# Rewards
from rewards.views import admin_rewards_list, admin_reward_action
test('Rewards Admin List', admin_rewards_list, user=admin)
rw_rec = User.objects.filter(rewards__isnull=False).first()
if rw_rec:
    rw = rw_rec.rewards.first()
    if rw:
        test('Reward Accept Action', admin_reward_action, 'POST',
             {'action':'accepted'}, admin, expect=302, path_args=[rw.pk])

# Support
from support.views import admin_inbox, admin_outbox, admin_reply
test('Support Admin Inbox', admin_inbox, user=admin)
test('Support Admin Outbox', admin_outbox, user=admin)
tkt_rec = User.objects.filter(tickets__isnull=False).first()
if tkt_rec:
    tkt = tkt_rec.tickets.first()
    if tkt:
        test('Support Reply', admin_reply, 'POST',
             {'reply':'Thanks'}, admin, expect=302, path_args=[tkt.pk])

# Notifications
from notifications.views import add_notification, add_qrcode
test('Notification Add', add_notification, user=admin)
test('QR Code Add', add_qrcode, user=admin)

# Products
from products.views import add_product, manage_products, project_settings, toggle_product_status
test('Product Add', add_product, user=admin)
test('Product Manage', manage_products, user=admin)
test('Product Settings', project_settings, user=admin)

# Reports
from reports.views import reports_index, export_members_excel, export_members_csv, export_members_pdf
test('Reports Index', reports_index, user=admin)
test('Members Excel', export_members_excel, user=admin)
test('Members CSV', export_members_csv, user=admin)
test('Members PDF', export_members_pdf, user=admin)

# ── USER TEMPLATE VIEWS ──
print('\n--- User Template Views ---')
from dashboard.views import user_dashboard
test('User Dashboard', user_dashboard, user=member)
from accounts.views import profile_view, edit_profile_view, change_password_view
test('Profile', profile_view, user=member)
test('Edit Profile GET', edit_profile_view, user=member)
test('Edit Profile POST', edit_profile_view, 'POST', {'email':'e@e.com'}, member, expect=302)
test('Change Password', change_password_view, user=member)
from kyc.views import kyc_submit_view, kyc_status_view
test('KYC Submit', kyc_submit_view, user=member)
test('KYC Status', kyc_status_view, user=member)
from network.views import referrals_view, tree_view
test('Referrals', referrals_view, user=member)
test('Tree View', tree_view, user=member)
from pmf.views import pmf_pay_view, pmf_history_view
test('PMF Pay', pmf_pay_view, user=member)
test('PMF History', pmf_history_view, user=member)
from helpdesk.views import send_help_view, send_help_history, receive_help_view, receive_help_history
test('Send Help', send_help_view, user=member)
test('Send History', send_help_history, user=member)
test('Receive Help', receive_help_view, user=member)
test('Receive History', receive_help_history, user=member)
from rewards.views import rewards_view
test('Rewards', rewards_view, user=member)
from support.views import ticket_create, inbox_view
test('Support Create', ticket_create, user=member)
test('Support Inbox', inbox_view, user=member)
from accounts.views import download_id_card, download_welcome_letter, download_joining_letter
test('ID Card', download_id_card, user=member)
test('Welcome Letter', download_welcome_letter, user=member)
test('Joining Letter', download_joining_letter, user=member)

# ── API VIEWS ──
print('\n--- API Views ---')
from accounts.views import RegisterAPIView, LoginAPIView, ProfileAPIView, ChangePasswordAPIView

import time
reg_username = f'vfy_{int(time.time())}'
reg_mobile = str(int(time.time()))[-10:]
r = rf.post('/api/register/', {'username':reg_username,'email':reg_username+'@v.com','mobile':reg_mobile,'password':'test123','password2':'test123'})
resp = RegisterAPIView.as_view()(r)
ok = resp.status_code == 201
if ok: passed += 1
else: failed += 1
print(f'  [{"PASS" if ok else "FAIL"}] API Register ({resp.status_code})')

r = rf.post('/api/login/', {'username':'rahul','password':'test123'})
resp = LoginAPIView.as_view()(r)
print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API Login ({resp.status_code})')
if resp.status_code == 200:
    r = rf.get('/api/profile/'); force_authenticate(r, user=member)
    resp = ProfileAPIView.as_view()(r)
    print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API Profile ({resp.status_code})')

from kyc.views import KYCListAPIView; r = rf.get('/kyc/api/list/'); force_authenticate(r, user=admin)
resp = KYCListAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API KYC List ({resp.status_code})')
from pmf.views import PMFListAPIView; r = rf.get('/pmf/api/list/'); force_authenticate(r, user=admin)
resp = PMFListAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API PMF List ({resp.status_code})')
from network.views import TreeAPIView; r = rf.get('/network/api/tree/'); force_authenticate(r, user=member)
resp = TreeAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API Tree ({resp.status_code})')
from rewards.views import RewardListAPIView; r = rf.get('/rewards/api/list/'); force_authenticate(r, user=member)
resp = RewardListAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API Rewards ({resp.status_code})')
from notifications.views import NotificationListAPIView, QRCodeListAPIView
r = rf.get('/notifications/api/list/'); force_authenticate(r, user=member)
resp = NotificationListAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API Notifications ({resp.status_code})')
r = rf.get('/notifications/api/qrcodes/'); force_authenticate(r, user=member)
resp = QRCodeListAPIView.as_view()(r); print(f'  [{"PASS" if resp.status_code==200 else "FAIL"}] API QR Codes ({resp.status_code})')

# ── TEMPLATE LOADING ──
print('\n--- Template Loading ---')
templates = ['base/base.html','base/sidebar_admin.html','base/sidebar_user.html',
    'accounts/login.html','accounts/profile.html','accounts/edit_profile.html','accounts/change_password.html','accounts/associate_list.html',
    'dashboard/admin_dashboard.html','dashboard/user_dashboard.html',
    'kyc/submit.html','kyc/status.html','kyc/admin_list.html',
    'pmf/pay.html','pmf/history.html','pmf/admin_list.html',
    'helpdesk/send_help.html','helpdesk/send_history.html','helpdesk/receive_help.html','helpdesk/receive_history.html','helpdesk/admin_list.html',
    'network/referrals.html','network/tree.html','network/tree_node.html',
    'notifications/add.html','notifications/qrcode.html',
    'products/add.html','products/edit.html','products/manage.html','products/settings.html',
    'rewards/list.html','rewards/admin_list.html',
    'support/create.html','support/inbox.html','support/admin_inbox.html','support/admin_outbox.html',
    'reports/index.html']
for t in templates:
    try: get_template(t); passed += 1; print(f'  [PASS] {t}')
    except: failed += 1; print(f'  [FAIL] {t}')

# ── STATIC FILES ──
print('\n--- Static Files ---')
for sf in ['css/style.css']:
    p = os.path.join(settings.BASE_DIR, 'static', sf)
    ok = os.path.exists(p)
    if ok: passed += 1
    else: failed += 1
    print(f'  [{"PASS" if ok else "FAIL"}] {sf}')

print(f'\nResults: {passed} passed, {failed} failed, {passed+failed} total')
