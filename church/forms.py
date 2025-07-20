from .models import ChurchStaffMember, StaffPayment
from .models import LicenseKey
from .models import Advertisement
from django.utils import timezone
from .models import PrayerRequest
import datetime
from .models import BibleReadingPlan
from .models import Event
from .models import OnlineGiving
from .models import ChatRoom, LiveStream
from .models import SundayIncomeReceipt
from django import forms
from .models import StewardshipRecord
from .models import CustomUser, Member, Church, Volunteer
from django.contrib.auth.forms import AuthenticationForm
from .models import Member
from .models import CustomUser, Member, MemberCategory, SEX_CHOICES, MARITAL_STATUS_CHOICES, Church
from django.core.exceptions import ValidationError



class ChurchRegistrationForm(forms.ModelForm):
    email_address     = forms.EmailField(label="Church Email")
    password          = forms.CharField(widget=forms.PasswordInput)
    confirm_password  = forms.CharField(widget=forms.PasswordInput)
    # 🔑 NEW
    license_key       = forms.CharField(label="License Key")

    class Meta:
        model  = Church
        fields = [
            'church_name', 'church_address', 'phone_number',
            'district', 'state', 'postal_code', 'country',
            'license_key',                       # ← keep order as you like
        ]

    def clean(self):
        cleaned = super().clean()

        # password match check
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Password and Confirm Password do not match.")

        # no key‐format check here (that’s done in the view so we can flag “already used”)
        return cleaned



class ChurchAdminLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        from .models import CustomUser  # import locally to avoid circular imports
        user = None

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_church_admin:
                    raise forms.ValidationError("This user is not a church admin.")
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid credentials.")
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("User with this email does not exist.")
        else:
            raise forms.ValidationError("Both email and password are required.")

        return cleaned_data

def church_admin_login(request):
    if request.method == 'POST':
        form = ChurchAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('church:church_dashboard')  # or wherever you want to redirect after successful login
            else:
                form.add_error(None, "Invalid email or password.")
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            form.add_error(None, "Invalid form input.")
    else:
        form = ChurchAdminLoginForm()

    return render(request, 'church/church_admin_login.html', {'form': form})

class ChurchImageForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = ['profile_picture']



SEX_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
MARITAL_STATUS_CHOICES = [('Single', 'Single'), ('Married', 'Married')]

class MemberRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    church = forms.ModelChoiceField(queryset=Church.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError("This phone number is already in use.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.email = self.cleaned_data.get('email')
        user.is_member = True

        if commit:
            user.save()
            member = Member(
                user=user,
                church=self.cleaned_data['church'],
                sex=self.cleaned_data['sex'],
                marital_status=self.cleaned_data['marital_status'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                address=self.cleaned_data['address'],
                profile_picture=self.cleaned_data.get('profile_picture')  # NEW FIELD
            )
            member.save()
        return user



class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['can_manage_members', 'can_manage_streams', 'can_manage_chats', 'can_manage_announcements']



class VolunteerCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    can_manage_members = forms.BooleanField(required=False)
    can_manage_streams = forms.BooleanField(required=False)
    can_manage_chats = forms.BooleanField(required=False)
    can_manage_announcements = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        return user



class StewardshipRecordForm(forms.ModelForm):
    class Meta:
        model = StewardshipRecord
        fields = ['transaction_type', 'category', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically limit categories based on transaction_type
        if self.instance and self.instance.transaction_type:
            self.fields['category'].choices = [
                choice for choice in self.fields['category'].choices
                if self._is_category_valid(choice[0], self.instance.transaction_type)
            ]

    def _is_category_valid(self, category, transaction_type):
        income_categories = ['tithe', 'inkind', 'thanksgiving', 'donation', 'opening']
        expense_categories = ['staff', 'facilities', 'ministry', 'admin', 'travel', 'reserve', 'stationery', 'misc', 'charity']
        return (
            transaction_type == 'IN' and category in income_categories
        ) or (
            transaction_type == 'EX' and category in expense_categories
        )


class StewardshipForm(forms.ModelForm):
    class Meta:
        model = StewardshipRecord
        exclude = ['church', 'is_trashed', 'trashed_at', 'created_at']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class SundayIncomeReceiptForm(forms.ModelForm):
    digital_signature = forms.ImageField(
        required=False,
        label='Digital Signature (Receiver)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )

    receiver_name = forms.CharField(
        required=False,
        label='Received By (Church Name)',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    phone_number = forms.CharField(
        required=False,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter giver\'s phone number (optional)',
        })
    )

    class Meta:
        model = SundayIncomeReceipt
        exclude = ['church', 'received_by']  # ✅ 'phone_number' is included automatically
        labels = {
            'name': 'Name',
            'amount': 'Amount (₦)',
            'category': 'Category',
            'thank_you_message': 'Thank You Message',
        }
        widgets = {
            'category': forms.Select(choices=[
                ('tithes', 'Tithes'),
                ('in_kind', 'In-kind'),
                ('thanksgiving', 'Thanksgiving'),
                ('offering', 'Offering'),
            ]),
            'thank_you_message': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class BibleReadingPlanForm(forms.ModelForm):
    class Meta:
        model = BibleReadingPlan
        fields = ['title', 'scripture_reference', 'reading_date']
        widgets = {
            'reading_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'scripture_reference': 'Scripture Reference',
            'reading_date': 'Reading Date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reading_date'].initial = datetime.date.today



class SundayReceiptFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ChoiceField(
        choices=[('', 'All'), ('tithes', 'Tithes'), ('offering', 'Offering'), ('thanksgiving', 'Thanksgiving'), ('in_kind', 'In-kind')],
        required=False
    )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_datetime', 'end_datetime', 'location', 'description', 'is_public']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name', 'livestream']

    def __init__(self, *args, **kwargs):
        church = kwargs.pop('church', None)
        super().__init__(*args, **kwargs)
        if church:
            self.fields['livestream'].queryset = LiveStream.objects.filter(church=church, is_active=True)
        self.fields['livestream'].empty_label = "No livestream available"


class LiveStreamForm(forms.ModelForm):
    class Meta:
        model = LiveStream
        fields = ['title', 'video_url', 'description', 'date', 'start_time', 'end_time', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,  # trimmed text box
                'style': 'max-width: 400px;',  # optional width constraint
                'placeholder': 'Enter a brief description...'
            }),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OnlineGivingForm(forms.ModelForm):
    class Meta:
        model = OnlineGiving
        fields = [
            'giver_name',
            'phone_number',
            'category',  # ✅ not 'purpose'
            'amount',
            'upi_transaction_id',  # ✅ this must be included
            'thank_you_message',
        ]
        widgets = {
            'thank_you_message': forms.TextInput(attrs={'placeholder': 'Optional message of gratitude'}),
        }



class ChurchOnlineGivingForm(forms.ModelForm):
    """Form used by church admin to update UPI ID and QR Code."""
    class Meta:
        model = Church
        fields = ['upi_id', 'qr_code']




class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter prayer title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your prayer request...', 'rows': 4}),
        }



class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['image', 'link_url', 'description']



class LicenseValidationForm(forms.Form):
    license_key = forms.CharField(label="License Key", max_length=100)

    def clean_license_key(self):
        key = self.cleaned_data['license_key']
        try:
            license = LicenseKey.objects.get(key=key, is_active=False)
            if license.is_expired():
                raise forms.ValidationError("This license key has expired.")
        except LicenseKey.DoesNotExist:
            raise forms.ValidationError("Invalid or already used license key.")
        return key



class ChurchStaffMemberForm(forms.ModelForm):
    class Meta:
        model = ChurchStaffMember
        fields = ['role', 'full_name', 'contact_number', 'photo', 'joined_on', 'monthly_salary', 'is_active']
        widgets = {
            'joined_on': forms.DateInput(attrs={'type': 'date'}),
        }

class StaffPaymentForm(forms.ModelForm):
    payment_month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Payment Date (e.g., 2025-07-01)",
        help_text="Select the full date for the payment month"
    )

    class Meta:
        model = StaffPayment
        fields = ['staff', 'amount', 'payment_month', 'remarks']
        # ✅ 'church' and 'paid_on' are excluded because:
        # - 'church' is set from the view
        # - 'paid_on' is auto-set via auto_now_add

    def __init__(self, *args, **kwargs):
        church = kwargs.pop('church', None)  # ✅ Extract 'church' safely
        super().__init__(*args, **kwargs)

        if church:
            self.fields['staff'].queryset = ChurchStaffMember.objects.filter(church=church)