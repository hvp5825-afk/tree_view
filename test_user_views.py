import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treeview_project.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django; django.setup()
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.filter(is_staff=False).first()
print('Testing with:', user.member_id, user.username)

factory = RequestFactory()

from dashboard.views import user_dashboard
from accounts.views import profile_view, edit_profile_view, change_password_view
from kyc.views import kyc_submit_view, kyc_status_view
from network.views import referrals_view, tree_view
from pmf.views import pmf_pay_view, pmf_history_view
from helpdesk.views import send_help_view, send_help_history, receive_help_view, receive_help_history
from rewards.views import rewards_view
from support.views import ticket_create, inbox_view

views = [
    ('Dashboard', user_dashboard),
    ('Profile', profile_view),
    ('Edit Profile', edit_profile_view),
    ('Change Password', change_password_view),
    ('KYC Submit', kyc_submit_view),
    ('KYC Status', kyc_status_view),
    ('Referrals', referrals_view),
    ('Tree View', tree_view),
    ('PMF Pay', pmf_pay_view),
    ('PMF History', pmf_history_view),
    ('Send Help', send_help_view),
    ('Send History', send_help_history),
    ('Receive Help', receive_help_view),
    ('Receive History', receive_help_history),
    ('Rewards', rewards_view),
    ('Support Create', ticket_create),
    ('Support Inbox', inbox_view),
]

for name, view in views:
    request = factory.get('/')
    request.user = user
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    try:
        response = view(request)
        status = response.status_code
        ok = 'OK' if status == 200 else 'FAIL'
        print(f'  [{ok}] {name} ({status})')
    except Exception as e:
        print(f'  [ERR] {name}: {e}')
