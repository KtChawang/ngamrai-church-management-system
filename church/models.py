from dateutil.relativedelta import relativedelta
import json
from django.utils.timezone import now
import random
import string
from datetime import timedelta
from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.apps import apps
from django.conf import settings


def some_function():
    Church = apps.get_model('church', 'Church')


# Define the SEX_CHOICES
SEX_CHOICES = (('M', 'Male'), ('F', 'Female'))
MARITAL_STATUS_CHOICES = (('S', 'Single'), ('M', 'Married'))

# === Custom User Manager ===
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# === Custom User ===
class CustomUser(AbstractUser):
    username = None  # Disable default username

    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    church = models.ForeignKey('Church', on_delete=models.CASCADE, related_name='members', blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True)

    is_church_admin = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def is_volunteer_with_permission(self, permission_flag: str) -> bool:
        if not self.is_volunteer:
            return False
        volunteer = getattr(self, 'volunteer', None)
        return getattr(volunteer, permission_flag, False) if volunteer else False

# === Church ===
class Church(models.Model):
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # 🔒 Prevent accidental deletion
        related_name='church_admin',
        null=True,
        blank=True,
    )

    church_name     = models.CharField(max_length=255)
    church_address  = models.CharField(max_length=255)
    phone_number    = models.CharField(max_length=20, unique=True)
    email_address   = models.EmailField(unique=True)
    district        = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    postal_code     = models.CharField(max_length=20)
    country         = models.CharField(max_length=100)
    profile_picture = models.ImageField(
        upload_to='church_profiles/', blank=True, null=True
    )

    # ✅ UPI details (already present)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # ✅ QR Code for UPI (NEW)
    qr_code = models.ImageField(
        upload_to='church_qrcodes/', blank=True, null=True
    )

    # ✅ Soft suspension flag
    is_suspended = models.BooleanField(
        default=False,
        help_text="Tick to disable all log‑ins for this church until dues are paid."
    )

    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.church_name




User = get_user_model()

# === Church Admin Profile ===
class ChurchAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='admin_profiles/', blank=True, null=True)
    church = models.OneToOneField('Church', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

class MemberCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    church = models.ForeignKey('Church', on_delete=models.CASCADE, null=True, blank=True)  # ← Make optional for now

    def __str__(self):
        return self.name

class Member(models.Model):
    SEX_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('Married', 'Married'),
        ('Single', 'Single'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    church = models.ForeignKey('Church', on_delete=models.CASCADE)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    date_of_birth = models.DateField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    category = models.ForeignKey(MemberCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def assign_society(self):
        if self.marital_status == 'Single':
            return 'Youth Society'
        elif self.marital_status == 'Married' and self.sex == 'Male':
            return 'Men Society'
        elif self.marital_status == 'Married' and self.sex == 'Female':
            return 'Women Society'
        else:
            return 'Youth Society' 

    def save(self, *args, **kwargs):
        # Assign society based on sex and marital status
        society_name = self.assign_society()
        category, created = MemberCategory.objects.get_or_create(
            name=society_name,
            church=self.church,
            defaults={'description': f'{society_name} for {self.church.church_name}'}

        )
        self.category = category
        super().save(*args, **kwargs)

    @property
    def email(self):
        return self.user.email


# === Volunteer Model ===
class Volunteer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)

    can_manage_members = models.BooleanField(default=False)
    can_manage_streams = models.BooleanField(default=False)
    can_manage_chats = models.BooleanField(default=False)
    can_manage_announcements = models.BooleanField(default=False)

    def __str__(self):
        return f"Volunteer: {self.user.email} ({self.church.church_name})"


# Event Model
class Event(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)  # Optional: control visibility

    def __str__(self):
        return f"{self.title} ({self.start_datetime.date()})"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    church = models.ForeignKey(Church, on_delete=models.CASCADE)  # Optional but recommended
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.event.title if self.event else ''}"



User = settings.AUTH_USER_MODEL

class Announcement(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)  # Announcement message
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notification-type behavior
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_announcements', null=True, blank=True, help_text="Leave blank for public announcements.")
    is_public = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)  # Only for personal announcements
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_notification(self):
        return self.user is not None and not self.is_public

    def __str__(self):
        return f"{self.title} ({'Notification' if self.is_notification() else 'Announcement'})"



# LiveStream Model
class LiveStream(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    description = models.TextField(blank=True, null=True)

    # ✅ New Fields
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)

    # ✅ Keep existing `date` for compatibility
    date = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_upcoming(self):
        return self.start_time > timezone.now()

    def is_live_now(self):
        now = timezone.now()
        end = self.end_time if self.end_time else self.start_time + timedelta(hours=2)
        return self.start_time <= now <= end

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

# Helper function
def get_default_church():
    return Church.objects.first()


# ChatRoom Model (linked to livestream)
class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    church = models.ForeignKey('Church', on_delete=models.CASCADE, default=get_default_church)
    livestream = models.OneToOneField('LiveStream', on_delete=models.CASCADE, related_name='chat_room', null=True, blank=True)

    def __str__(self):
        return self.name

# Chat Message Model
class Message(models.Model):
    content = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'


class StewardshipRecord(models.Model):
    INCOME = 'IN'
    EXPENSE = 'EX'
    OPENING = 'OP'

    TRANSACTION_TYPES = [
        (OPENING, 'Opening Balance'),
        (INCOME, 'Income'),
        (EXPENSE, 'Expenditure'),
    ]

    CATEGORY_CHOICES = [
        ('opening_balance', 'Opening Balance'),
        ('sunday_income', 'Sunday Income'),
        ('thanksgiving', 'Thanksgiving'),
        ('donation', 'Donation'),
        ('mission_offering', 'Mission Offering'),
        ('investment_return', 'Investment Return'),
        ('rental_income', 'Rental Income'),
        ('staff', 'Staff Salary/Allowance'),
        ('facilities', 'Facilities and Maintenance'),
        ('ministry', 'Ministry and Outreach'),
        ('mission_support', 'Mission Support'),
        ('admin', 'Administrative Costs'),
        ('travel', 'Travel and Conferences'),
        ('stationery', 'Stationery'),
        ('charity', 'Charity Fund'),
        ('reserve', 'Reserve and Emergency Fund'),
        ('misc', 'Miscellaneous'),
    ]

    church = models.ForeignKey('Church', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    is_trashed = models.BooleanField(default=False)
    trashed_at = models.DateTimeField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False, user=None):
        self.is_trashed = True
        self.trashed_at = timezone.now()
        self.save()

        AuditLog.objects.create(
            action='Soft Delete',
            user=user,
            content_type='StewardshipRecord',
            object_id=self.pk,
            object_repr=str(self),
            changes='Marked as trashed.'
        )

    def restore(self, user=None):
        self.is_trashed = False
        self.trashed_at = None
        self.save()

        AuditLog.objects.create(
            action='Restore',
            user=user,
            content_type='StewardshipRecord',
            object_id=self.pk,
            object_repr=str(self),
            changes='Restored from trash.'
        )

    def hard_delete(self, using=None, keep_parents=False, user=None):
        AuditLog.objects.create(
            action='Hard Delete',
            user=user,
            content_type='StewardshipRecord',
            object_id=self.pk,
            object_repr=str(self),
            changes='Permanently deleted.'
        )
        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.get_category_display()} - ₹{self.amount} on {self.date}"



# models.py
class AuditLog(models.Model):
    stewardship_record = models.ForeignKey(
    StewardshipRecord,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=50)  # e.g., Created, Updated, Deleted
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action} by {self.user or 'System'}"


class SundayIncomeReceipt(models.Model):
    CATEGORY_CHOICES = [
        ('offering', 'Offering'),
        ('tithe', 'Tithe'),
        ('donation', 'Donation'),
        ('thanksgiving', 'Thanksgiving'),
        ('other', 'Other'),
    ]

    church = models.ForeignKey('Church', on_delete=models.CASCADE, related_name='income_receipts')
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)  # ✅ Updated
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    thank_you_message = models.CharField(max_length=255, blank=True, null=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_income_receipts'
    )

    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    digital_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        force = kwargs.pop('force', False)
        if force:
            return super().delete(*args, **kwargs)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if not self.receipt_number:
            self.receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

        if is_new:
            verify_url = reverse('church:verify_receipt', args=[self.receipt_number])
            full_url = f'https://yourdomain.com{verify_url}'
            qr_img = qrcode.make(full_url)
            qr_io = BytesIO()
            qr_img.save(qr_io, format='PNG')
            qr_filename = f'{self.receipt_number}.png'
            self.qr_code.save(qr_filename, ContentFile(qr_io.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

    def regenerate_qr_code(self):
        verify_url = reverse('verify_receipt', args=[self.receipt_number])
        full_url = f'https://yourdomain.com{verify_url}'
        qr_img = qrcode.make(full_url)
        qr_io = BytesIO()
        qr_img.save(qr_io, format='PNG')
        qr_filename = f'{self.receipt_number}_regenerated.png'
        self.qr_code.save(qr_filename, ContentFile(qr_io.getvalue()), save=False)
        self.save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.receipt_number} - {self.name}"



class OnlineGiving(models.Model):
    GIVING_CATEGORIES = [
        ('tithes', 'Tithes'),
        ('thanks', 'Thanks'),
        ('offering', 'Offering'),
        ('donation', 'Donation'),
    ]

    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    giver_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_transaction_id = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20, choices=GIVING_CATEGORIES, default='tithes'
    )
    thank_you_message = models.CharField(max_length=255, default="Thank you for your generosity!")
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW FIELDS
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    # qr_code = models.ImageField(upload_to='receipts/qrcodes/', blank=True, null=True)  # Optional for future

    def __str__(self):
        return f"{self.giver_name} gave ₹{self.amount} for {self.get_category_display()}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        prefix = 'OG'
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}-{date_part}-{random_part}"

    @property
    def display_receiver(self):
        if self.church and self.church.upi_id:
            return self.church.upi_id
        elif self.church:
            return self.church.church_name
        return "—"


class SMSLog(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    sent_at = models.DateTimeField(default=now)
    success = models.BooleanField(default=False)
    sms_type = models.CharField(max_length=50, default="general")
    sender = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"SMS to {self.phone_number} on {self.sent_at.strftime('%Y-%m-%d %H:%M')}"



class BibleReadingPlan(models.Model):
    church = models.ForeignKey('Church', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    scripture_reference = models.CharField(max_length=255)
    content = models.TextField()
    reading_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reading_date']
        unique_together = ('church', 'reading_date')

    def __str__(self):
        return f"{self.title} ({self.reading_date})"

         

class MemberReadingLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    reading_plan = models.ForeignKey(BibleReadingPlan, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'reading_plan')

    def __str__(self):
        return f"{self.member} read on {self.completed_at.date()}"



class ActivityLog(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class PrayerRequestQuerySet(models.QuerySet):
    def active(self):
        """Return only requests from the last 24 hours."""
        cutoff = timezone.now() - timedelta(hours=24)
        return self.filter(created_at__gte=cutoff)

class PrayerRequest(models.Model):
    member      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    # hook up the custom QuerySet
    objects = PrayerRequestQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.member}"



class Advertisement(models.Model):
    image = models.ImageField(upload_to='ads/')
    link_url = models.URLField()
    description = models.TextField()
    is_approved = models.BooleanField(default=False)  # manual approval
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ad to {self.link_url} (Approved: {self.is_approved})"



class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    photo = models.ImageField(upload_to='testimonials/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChairmanMessage(models.Model):
    title = models.CharField(max_length=200, default="Message from the Chairman's Desk")
    message = models.TextField()
    photo = models.ImageField(upload_to='chairman/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LicenseKey(models.Model):
    # ── ORIGINAL FIELDS (unchanged) ───────────────────────────────
    key = models.CharField(max_length=100, unique=True)
    church_name = models.CharField(max_length=255, blank=True, null=True)
    issued_to_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=False)          # stays!
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    # ── NEW FIELDS (minimal additions) ────────────────────────────
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("pro", "Pro"),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="basic")

    # one license ↔︎ one church after activation
    church = models.OneToOneField(
        "Church",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="license",
    )
    activated_at = models.DateTimeField(null=True, blank=True)

    # ── HELPERS ───────────────────────────────────────────────────
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def is_valid(self):
        """
        A key is valid if:
          • not already linked to a church (is_active == False)
          • and not expired
        """
        return (not self.is_active) and (not self.is_expired())

    def __str__(self):
        status = "USED" if self.is_active else "UNUSED"
        return f"{self.key} – {status}"




class SubscriptionQuerySet(models.QuerySet):
    def upcoming(self, days=7):
        today  = timezone.now().date()
        return (
            self.filter(is_active=True,
                        next_due_date__range=(today, today + timedelta(days=days)))
                .select_related("church")
                .order_by("next_due_date")
        )


class Subscription(models.Model):
    PLAN_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    # ── core fields ──────────────────────────────────────────
    church        = models.OneToOneField(
        "Church",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    is_active     = models.BooleanField(default=True)
    last_paid_at  = models.DateField(null=True, blank=True)   # allow blank on first save
    next_due_date = models.DateField(null=True, blank=True)
    plan          = models.CharField(max_length=20, choices=PLAN_CHOICES, default="monthly")
    amount        = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # ── manual‑payment workflow additions ───────────────────
    payment_note  = models.TextField(blank=True, null=True)           # UPI ref / remarks
    confirmed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_subscriptions",
    )
    confirmed_at  = models.DateTimeField(null=True, blank=True)

    # ── helpers ──────────────────────────────────────────────
    def is_overdue(self):
        """Returns True if subscription is inactive or its due‑date has passed."""
        return (not self.is_active) or (
            self.next_due_date and timezone.now().date() > self.next_due_date
        )

    def confirm_payment(self, admin_user=None, note: str = ""):
        """
        Manually mark a UPI payment as received and reactivate the church.

        Args:
            admin_user (User | None): Admin confirming the payment.
            note (str): Optional UPI transaction reference or remarks.
        """
        today = timezone.now().date()

        # 1️⃣  Record payment details
        self.last_paid_at = today
        self.payment_note = note
        self.confirmed_by = admin_user
        self.confirmed_at = timezone.now()

        # 2️⃣  Compute the next due date from plan
        self.next_due_date = (
            today + relativedelta(months=1)
            if self.plan == "monthly"
            else today + relativedelta(years=1)
        )

        # 3️⃣  Reactivate subscription & church
        self.is_active = True
        if self.church_id:
            self.church.is_suspended = False
            self.church.save(update_fields=["is_suspended"])

        # 4️⃣  Persist only the fields we changed
        self.save(
            update_fields=[
                "last_paid_at",
                "next_due_date",
                "payment_note",
                "confirmed_by",
                "confirmed_at",
                "is_active",
            ]
        )

    # ── custom save ──────────────────────────────────────────
    def save(self, *args, **kwargs):
        # 1️⃣  Ensure last‑paid date is set the first time
        if self.last_paid_at is None:
            self.last_paid_at = timezone.now().date()

        # 2️⃣  Compute the next due date from plan
        if self.plan == "monthly":
            self.next_due_date = self.last_paid_at + relativedelta(months=1)
        elif self.plan == "yearly":
            self.next_due_date = self.last_paid_at + relativedelta(years=1)

        # 3️⃣  Auto‑suspend / unsuspend the church
        if self.church_id:
            self.church.is_suspended = self.is_overdue()
            self.church.save(update_fields=["is_suspended"])

        super().save(*args, **kwargs)

    # ── display ──────────────────────────────────────────────
    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"{self.church.church_name} – {self.plan} – {status}"



class PaymentQRCode(models.Model):
    title = models.CharField(max_length=100, default="UPI Payment")
    upi_id = models.CharField(max_length=100, help_text="e.g., yourname@upi")
    qr_image = models.ImageField(upload_to='payment_qr/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.upi_id}"



# church/models.py
class MemberChatMessage(models.Model):
    church  = models.ForeignKey(Church, on_delete=models.CASCADE)
    sender  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    # moderation fields
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        permissions = [
            ("moderate_message", "Can moderate member chat messages")
        ]

    def __str__(self):
        return f"{self.sender} - {self.content[:30]}"



STAFF_ROLE_CHOICES = [
    ('pastor', 'Pastor'),
    ('associate_pastor', 'Associate Pastor'),
    ('elder', 'Elder'),
    ('deacon', 'Deacon'),
    ('head_deacon', 'Head Deacon'),
    ('deaconess', 'Deaconess'),
    ('clerk', 'Clerk / Secretary'),
    ('choir_master', 'Choir Master / Song Leader'),
    ('pianist', 'Pianist'),
    ('drummer', 'Drummer'),
    ('guitarist', 'Guitarist'),
    ('auditor', 'Auditor'),
    ('sound_technician', 'Sound Technician'),
    ('projector_operator', 'Projector Operator'),
    ('security', 'Chowkidar / Security'),
    ('cleaner', 'Cleaner / Janitor'),
    ('groundskeeper', 'Groundskeeper'),
    ('sunday_school_superintendent', 'Sunday School Superintendent'),
    ('sunday_school_teacher', 'Sunday School Teacher'),  # ✅ NEW
    ('other', 'Other'),
]

class ChurchStaffMember(models.Model):
    church = models.ForeignKey('Church', on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=30, choices=STAFF_ROLE_CHOICES)
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)

    joined_on = models.DateField(null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()}) - {self.church.church_name}"


class StaffPayment(models.Model):
    staff = models.ForeignKey(ChurchStaffMember, on_delete=models.CASCADE, related_name='payments')
    church = models.ForeignKey(Church, on_delete=models.CASCADE)  # newly added field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_month = models.DateField(help_text="Use the 1st of the month to represent the payment period.")
    paid_on = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)


class ChurchGalleryImage(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='church_gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title






