from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from network.models import Referral
from kyc.models import KYCRequest
from pmf.models import PMFRequest
from helpdesk.models import SendHelpRequest, ReceiveHelpRequest
from rewards.models import Reward
from support.models import SupportTicket
from notifications.models import Notification, QRCode
from products.models import Product, ProjectSetting
import random, string
from datetime import timedelta

User = get_user_model()


def rand_member():
    return 'U' + ''.join(random.choices(string.digits, k=5))


def rand_phone():
    return '9' + ''.join(random.choices(string.digits, k=9))


class Command(BaseCommand):
    help = 'Seed test data for all modules'

    def handle(self, *args, **options):
        self.stdout.write('Seeding test data...')

        # ── Create superuser if not exists ──
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
            self.stdout.write('  Superuser created: admin / admin123')

        # ── Products ──
        products_data = [
            {'title': 'Health Supplement', 'amount': 1500, 'color': 'Red', 'size': '500ml', 'details': '<p>Premium health supplement</p>'},
            {'title': 'Herbal Tea Pack', 'amount': 800, 'color': 'Green', 'size': '250g', 'details': '<p>Organic herbal tea blend</p>'},
            {'title': 'Fitness Band', 'amount': 2500, 'color': 'Black', 'size': 'One Size', 'details': '<p>Smart fitness tracker</p>'},
            {'title': 'Essential Oil Kit', 'amount': 1200, 'color': 'Brown', 'size': '10ml x 6', 'details': '<p>Aromatherapy oil collection</p>'},
            {'title': 'Protein Powder', 'amount': 2000, 'color': 'White', 'size': '1kg', 'details': '<p>Whey protein isolate</p>'},
        ]
        for pd in products_data:
            Product.objects.get_or_create(title=pd['title'], defaults=pd)

        # ── Project Settings ──
        settings_data = [
            {'title': 'Level 1 Commission', 'amount': 500, 'mark': '5%', 'reward': 'Cash'},
            {'title': 'Level 2 Commission', 'amount': 300, 'mark': '3%', 'reward': 'Cash'},
            {'title': 'Binary Commission', 'amount': 1000, 'mark': '10%', 'reward': 'Cash'},
            {'title': 'Leadership Bonus', 'amount': 5000, 'mark': 'Top Performer', 'reward': 'Product'},
        ]
        for sd in settings_data:
            ProjectSetting.objects.get_or_create(title=sd['title'], defaults=sd)

        # ── Create member users in binary tree ──
        admin = User.objects.filter(is_superuser=True).first()
        members = []
        member_data = [
            ('Rahul Sharma', 'rahul', 'rahul@test.com'),
            ('Priya Patel', 'priya', 'priya@test.com'),
            ('Amit Singh', 'amit', 'amit@test.com'),
            ('Sneha Gupta', 'sneha', 'sneha@test.com'),
            ('Vikram Joshi', 'vikram', 'vikram@test.com'),
            ('Neha Verma', 'neha', 'neha@test.com'),
            ('Rajesh Kumar', 'rajesh', 'rajesh@test.com'),
            ('Pooja Mehta', 'pooja', 'pooja@test.com'),
            ('Ankit Tiwari', 'ankit', 'ankit@test.com'),
            ('Divya Nair', 'divya', 'divya@test.com'),
            ('Sandeep Yadav', 'sandeep', 'sandeep@test.com'),
            ('Kiran Desai', 'kiran', 'kiran@test.com'),
            ('Manoj Pillai', 'manoj', 'manoj@test.com'),
            ('Anjali Rao', 'anjali', 'anjali@test.com'),
            ('Deepak Chauhan', 'deepak', 'deepak@test.com'),
        ]

        for name, uname, email in member_data:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(
                    username=uname,
                    email=email,
                    mobile=rand_phone(),
                    password='test123',
                    status=random.choice(['active', 'inactive']),
                )
                u.plain_password = 'test123'
                u.save()
                profile, _ = UserProfile.objects.get_or_create(user=u)
                profile.first_name = name.split()[0]
                profile.last_name = name.split()[1] if len(name.split()) > 1 else ''
                profile.address = f'{random.randint(1,999)} Main Street, {random.choice(["Mumbai","Delhi","Bangalore","Pune","Chennai","Kolkata","Hyderabad","Ahmedabad"])}'
                profile.city = random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Chennai'])
                profile.state = random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat'])
                profile.country = 'India'
                profile.pincode = str(random.randint(100000, 999999))
                profile.bank_name = random.choice(['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB'])
                profile.account_holder = name
                profile.account_number = ''.join(random.choices(string.digits, k=12))
                profile.ifsc_code = random.choice(['SBIN0001234', 'HDFC0004321', 'ICIC0005678'])
                profile.gpay = rand_phone()
                profile.phonepe = rand_phone()
                profile.paytm = rand_phone()
                profile.upi_id = f'{uname}@paytm'
                profile.save()
                members.append(u)
                self.stdout.write(f'  Member created: {u.member_id} - {name} ({u.status})')
            else:
                u = User.objects.get(username=uname)
                members.append(u)

        # ── Create Referral (binary tree) ──
        if members:
            root = members[0]
            # first user has no sponsor
            for i, m in enumerate(members[1:], 1):
                if not Referral.objects.filter(member=m).exists():
                    # alternate between root and previous members
                    if i <= 2:
                        sponsor = root
                        parent = root
                        position = 'LEFT' if i == 1 else 'RIGHT'
                    else:
                        parent_idx = (i - 1) // 2
                        if parent_idx < len(members):
                            parent = members[parent_idx]
                        else:
                            parent = root
                        sponsor = members[random.randint(0, len(members) - 1)]
                        if sponsor == m:
                            sponsor = root
                        position = 'LEFT' if i % 2 == 0 else 'RIGHT'
                    Referral.objects.create(
                        sponsor=sponsor, member=m, parent=parent, position=position
                    )
            # Set sponsor_id on User model from Referral
            for ref in Referral.objects.select_related('sponsor', 'member'):
                ref.member.sponsor_id = ref.sponsor.member_id
                ref.member.save(update_fields=['sponsor_id'])
            self.stdout.write(f'  Created {len(members)-1} referrals in binary tree')

        # ── KYC Requests ──
        # Seed pending KYC requests for a richer pending-kyc list view
        pending_kyc_names = [
            ('Vikram Joshi', 'vikram', 'ABCDE1234F', '987654321012'),
            ('Neha Verma', 'neha', 'GHIJK5678L', '912345678901'),
            ('Rajesh Kumar', 'rajesh', 'MNOPQ9012R', '998877665544'),
            ('Pooja Mehta', 'pooja', 'ABCDE1234F', '887766554433'),
            ('Ankit Tiwari', 'ankit', 'GHIJK5678L', '776655443322'),
            ('Sandeep Yadav', 'sandeep', 'MNOPQ9012R', '665544332211'),
            ('Kiran Desai', 'kiran', 'ABCDE1234F', '554433221100'),
        ]
        for name, uname, pan, aadhaar in pending_kyc_names:
            try:
                u = User.objects.get(username=uname)
            except User.DoesNotExist:
                continue
            if not KYCRequest.objects.filter(user=u).exists():
                KYCRequest.objects.create(
                    user=u,
                    aadhaar_number=aadhaar,
                    pan_number=pan,
                    status='pending',
                    remarks='',
                    submitted_at=timezone.now() - timedelta(days=random.randint(1, 15)),
                    reviewed_at=None,
                )
                self.stdout.write(f'  KYC pending: {u.member_id} - {name}')

        # Some accepted/rejected KYC records (existing members not in pending list)
        for u in members:
            if not KYCRequest.objects.filter(user=u).exists():
                status = random.choice(['accepted', 'rejected'])
                KYCRequest.objects.create(
                    user=u,
                    aadhaar_number=str(random.randint(100000000000, 999999999999)),
                    pan_number=random.choice(['ABCDE1234F', 'GHIJK5678L', 'MNOPQ9012R']),
                    status=status,
                    remarks='' if status == 'accepted' else 'Document unclear, please resubmit',
                    submitted_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    reviewed_at=timezone.now() if status != 'pending' else None,
                )
        self.stdout.write('  KYC requests seeded')

        # ── PMF Requests ──
        for u in members[:6]:
            for level in range(1, 4):
                PMFRequest.objects.get_or_create(
                    user=u, level=level,
                    defaults={
                        'amount': level * 500,
                        'transaction_no': 'TXN' + str(random.randint(100000, 999999)),
                        'status': random.choice(['pending', 'product_accepted', 'accepted', 'rejected', 'dispatched']),
                        'created_at': timezone.now() - timedelta(days=level * 7),
                        'remarks': '' if random.random() > 0.3 else 'Payment verified',
                    }
                )
        self.stdout.write('  PMF requests seeded')

        # ── Helpdesk (Send/Receive) ──
        for i, u in enumerate(members[:5]):
            for _ in range(2):
                receiver = members[(i + 1) % len(members)]
                SendHelpRequest.objects.get_or_create(
                    user=u, request_to=receiver, amount=random.choice([500, 1000, 1500, 2000]),
                    defaults={
                        'payment_method': random.choice(['gpay', 'phonepe', 'paytm', 'upi', 'bank']),
                        'transaction_no': 'TXN' + str(random.randint(100000, 999999)),
                        'status': random.choice(['pending', 'accepted', 'rejected']),
                        'created_at': timezone.now() - timedelta(days=random.randint(1, 15)),
                        'remarks': '',
                    }
                )
            ReceiveHelpRequest.objects.get_or_create(
                user=u, amount=random.choice([1000, 2000]),
                defaults={
                    'status': random.choice(['pending', 'accepted', 'rejected']),
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 10)),
                }
            )
        self.stdout.write('  Help requests seeded')

        # ── Rewards ──
        for u in members[:5]:
            for rtype in ['product', 'cash']:
                Reward.objects.get_or_create(
                    user=u, reward_name=random.choice(['Top Recruiter', 'Leadership', 'Performance Star', 'Binary Bonus']),
                    reward_type=rtype,
                    defaults={
                        'reward_amount': random.randint(500, 5000),
                        'qualification_date': timezone.now() - timedelta(days=random.randint(1, 60)),
                        'status': random.choice(['pending', 'accepted', 'rejected']),
                    }
                )
        self.stdout.write('  Rewards seeded')

        # ── Support Tickets ──
        for u in members[:4]:
            SupportTicket.objects.create(
                user=u,
                subject=random.choice(['Payment issue', 'Login problem', 'KYC query', 'Product enquiry', 'Withdrawal help']),
                message=f'This is a test ticket from {u.get_full_name()} regarding {random.choice(["account access","payment delay","document update","product delivery"])}.',
                status=random.choice(['open', 'replied', 'closed']),
                reply='We are looking into it. Thank you for your patience.' if random.random() > 0.5 else '',
                created_at=timezone.now() - timedelta(days=random.randint(1, 20)),
            )
        self.stdout.write('  Support tickets seeded')

        # ── Notifications ──
        Notification.objects.get_or_create(
            notif_type='global', message='Welcome to TreeView MLM Platform! Start your journey today.',
            defaults={'is_read': False}
        )
        Notification.objects.get_or_create(
            notif_type='global', message='New product launch: Health Supplement now available.',
            defaults={'is_read': False}
        )
        for u in members[:2]:
            Notification.objects.get_or_create(
                user=u, notif_type='individual',
                message=f'Congratulations {u.get_full_name()}! You have earned a reward.',
                defaults={'is_read': False}
            )
        self.stdout.write('  Notifications seeded')

        # ── QR Codes ──
        QRCode.objects.get_or_create(
            title='Company GPay', qr_type='gpay',
            defaults={'bank_name': 'SBI', 'account_no': '1234567890', 'ifsc_code': 'SBIN0000123', 'account_holder': 'TreeView MLM'}
        )
        QRCode.objects.get_or_create(
            title='Company Bank Account', qr_type='bank',
            defaults={'bank_name': 'HDFC', 'account_no': '9876543210', 'ifsc_code': 'HDFC0004321', 'account_holder': 'TreeView MLM'}
        )
        self.stdout.write('  QR codes seeded')

        self.stdout.write(self.style.SUCCESS('Seed data complete!'))
