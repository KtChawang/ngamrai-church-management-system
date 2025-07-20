from .models import ChurchGalleryImage
from .models import PaymentQRCode
from .models import Subscription
from django.utils import timezone
from .models import LicenseKey
import secrets, string
from .models import ChairmanMessage
from .models import Testimonial
from .models import Advertisement
from django.urls import reverse
from django.contrib import admin
from .models import AuditLog
from django.urls import path
from .models import SundayIncomeReceipt
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, Church, Member, Event, LiveStream, Announcement

# ✅ Custom Admin for CustomUser (no username field)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_member', 'is_church_admin', 'is_active')
    list_filter = ('is_member', 'is_church_admin', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'sex', 'marital_status', 'church')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_member', 'is_church_admin', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'sex', 'marital_status', 'church', 'is_member', 'is_church_admin'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# ✅ Admin for Church
@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'phone_number', 'country', 'state', 'date_registered')
    search_fields = ('church_name', 'phone_number')

# ✅ Admin for Member
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'church')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('church',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if hasattr(request.user, 'churchadminprofile'):
            return queryset.filter(church=request.user.churchadminprofile.church)
        return queryset.none()

# ✅ Admin for Event
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'end_datetime', 'location', 'is_public', 'church')
    list_filter = ('church', 'is_public')
    search_fields = ('title', 'location')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if hasattr(request.user, 'churchadminprofile'):
            return queryset.filter(church=request.user.churchadminprofile.church)
        return queryset.none()


# ✅ Admin for LiveStream
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'church')
    search_fields = ('title', 'date')
    list_filter = ('church',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if hasattr(request.user, 'churchadminprofile'):
            return queryset.filter(church=request.user.churchadminprofile.church)
        return queryset.none()

# ✅ Admin for Announcement
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'church')
    search_fields = ('title', 'content')
    list_filter = ('church',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if hasattr(request.user, 'churchadminprofile'):
            return queryset.filter(church=request.user.churchadminprofile.church)
        return queryset.none()

def regenerate_qr_code_for_instance(instance):
    verify_url = reverse('verify_receipt', args=[instance.receipt_number])
    full_url = f'https://yourdomain.com{verify_url}'  # Replace with your real domain

    qr_img = qrcode.make(full_url)
    qr_io = BytesIO()
    qr_img.save(qr_io, format='PNG')

    qr_filename = f'{instance.receipt_number}.png'
    instance.qr_code.save(qr_filename, ContentFile(qr_io.getvalue()), save=False)
    instance.save(update_fields=['qr_code'])


@admin.action(description="Regenerate missing QR codes")
def regenerate_missing_qrs(modeladmin, request, queryset):
    count = 0
    for receipt in queryset:
        if not receipt.qr_code:
            regenerate_qr_code_for_instance(receipt)
            count += 1
    messages.success(request, f"Regenerated {count} QR code(s).")


@admin.register(SundayIncomeReceipt)
class SundayIncomeReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'name', 'category', 'amount', 'qr_code_preview', 'regenerate_qr_link')
    readonly_fields = ('qr_code_preview',)
    actions = [regenerate_missing_qrs]

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" height="60" />', obj.qr_code.url)
        return "No QR code"

    def regenerate_qr_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Regenerate QR</a>',
            reverse('admin:regenerate_qr_code', args=[obj.id])
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('regenerate-qr/<int:receipt_id>/', self.admin_site.admin_view(self.regenerate_qr_view), name='regenerate_qr_code'),
        ]
        return custom_urls + urls


    def regenerate_qr_view(self, request, receipt_id):
        receipt = get_object_or_404(SundayIncomeReceipt, id=receipt_id)
        regenerate_qr_code_for_instance(receipt)
        self.message_user(request, f"QR code regenerated for {receipt.receipt_number}")
        return redirect(request.META.get('HTTP_REFERER', '/admin/church/sundayincomereceipt/'))


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'stewardship_record', 'user', 'timestamp')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('message', 'user__email', 'stewardship_record__category')




@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('link_url', 'submitted_at', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('link_url', 'description')
    actions = ['approve_ads']

    def approve_ads(self, request, queryset):
        queryset.update(is_approved=True)
    approve_ads.short_description = "Mark selected ads as approved"



# ────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────
def _new_key(length: int = 24) -> str:
    """Generate a URL‑safe random key (letters+digits)."""
    alphabet = string.ascii_uppercase + string.digits
    # XXXXXXXXXXXXXXXXXXXXXXXX  (24 chars → ~125 bits of entropy)
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _pretty_status(lic: LicenseKey) -> str:
    """Return colour‑coded HTML for list_display."""
    if lic.is_expired():
        color, label = ("#dc3545", "Expired ❌")
    elif lic.is_active:
        color, label = ("#198754", "Used ✔")
    else:
        color, label = ("#0d6efd", "Unused")
    return format_html('<strong style="color:{}">{}</strong>', color, label)


# ─────────────────────────────────────────────────────
#  Admin
# ─────────────────────────────────────────────────────
@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "plan",
        "status_badge",
        "church_name",
        "issued_to_email",
        "expires_at",
    )
    list_filter = ("is_active", "plan", "expires_at")
    search_fields = ("key", "church_name", "issued_to_email")
    readonly_fields = ("issued_at", "activated_at", "status_badge")
    actions = ["generate_new_keys", "deactivate_selected"]

    actions_on_top = True
    actions_selection_counter = False 
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",            # leave blank → auto‑generated
                    "plan",
                    ("expires_at", "is_active"),
                    "notes",
                )
            },
        ),
        (
            "Binding info (filled automatically after activation)",
            {
                "fields": (
                    "status_badge",
                    "church",
                    "church_name",
                    "issued_to_email",
                    ("issued_at", "activated_at"),
                )
            },
        ),
    )

    # ── status badge column / read‑only field ──────────────────────
    @admin.display(description="Status", ordering="is_active")
    def status_badge(self, obj: LicenseKey):
        return _pretty_status(obj)

    # ── auto‑generate key on first save  +  auto‑stamp activation ──
    def save_model(self, request, obj, form, change):
        if not obj.key:
            obj.key = _new_key()
        # if admin toggles “is_active”, ensure timestamp is set/cleared
        if obj.is_active and obj.activated_at is None:
            obj.activated_at = timezone.now()
        elif not obj.is_active:
            obj.activated_at = None
            obj.church = None  # optional: unbind on manual deactivate
        super().save_model(request, obj, form, change)

    # ─────────────────────────── Actions ────────────────
    @admin.action(description="➕ Generate 10 fresh keys")
    def generate_new_keys(self, request, queryset):
        amount = 10
        objs = [
            LicenseKey(key=_new_key(), is_active=False)
            for _ in range(amount)
        ]
        LicenseKey.objects.bulk_create(objs)
        self.message_user(request, f"{amount} new license keys generated.")

    @admin.action(description="🚫 De‑activate selected keys")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(
            is_active=False,
            church=None,
            church_name=None,
            issued_to_email=None,
            activated_at=None,
        )
        self.message_user(request, f"{updated} key(s) de‑activated.")



@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "church",
        "plan",
        "amount",
        "last_paid_at",
        "next_due_date",
        "is_active",
        "overdue_status",
    )
    list_filter = ("plan", "is_active", "next_due_date")
    search_fields = ("church__church_name",)

    @admin.display(boolean=True, description="Overdue")
    def overdue_status(self, obj):
        return obj.is_overdue()


@admin.register(PaymentQRCode)
class PaymentQRCodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'upi_id', 'uploaded_at')
    search_fields = ('upi_id',)



# ✅ Register All Admins
admin.site.register(ChairmanMessage)
admin.site.register(Testimonial)
admin.site.register(Member, MemberAdmin)
admin.site.register(ChurchGalleryImage)



