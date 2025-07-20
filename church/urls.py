
from .views import (
    LiveStreamListView,
    LiveStreamCreateView,
    LiveStreamUpdateView,
    LiveStreamDeleteView,
    MemberLiveStreamListView,
    MemberLiveStreamDetailView,
    PostMessageView, fetch_messages
)
from .views import PrayerRequestListView, PrayerRequestCreateView
from django.urls import path
from .views import (
    AdminAnnouncementListView, AnnouncementCreateView,
    AnnouncementUpdateView, AnnouncementDeleteView,
    MemberAnnouncementListView, MarkAnnouncementReadView,          MemberAnnouncementDetailView
)
from .views import (
    OnlineGivingView,
    OnlineGivingReceiptView,
    PrintOnlineGivingReceiptView,
    DeleteOnlineGivingView,
)
from church.views import (
    MemberChatModerationListView,
    delete_member_chat_message, 
)
from .views import (
    BibleReadingPlanListView, BibleReadingPlanCreateView,
    BibleReadingPlanUpdateView, BibleReadingPlanDeleteView,
    MemberBibleReadingTodayView, MemberBibleReadingArchiveView,
    MarkReadingAsDoneView, MemberReadingProgressView,
    MemberActivityLogView,
)
from .views import staff_payment_list 
from .views import ChurchOnlineGivingView
from church.views import MemberChatModerationListView, delete_member_chat_message
from .views import PaymentInstructionsView
from church.views import ChatRoomUpdateView
from .views import generate_society_members_pdf
from .views import SMSLogListView, ResendSMSView
from .views import mark_all_notifications_as_read 
from .views import WatchLiveView, ChatRoomDeleteView
from .views import MemberProfileUpdateView
from .views import MemberLoginView, MemberDashboardView, member_logout
from .views import MemberRegistrationView
from .views import ChatRoomCreateView
from .views import LiveStreamDetailView
from .views import ChatRoomListView 
from .views import ChatRoomDetailView
from django.views.generic import TemplateView
from .views import EventListView, EventCreateView, EventUpdateView, EventDeleteView,  all_notifications
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings  # ✅ Needed for media files
from django.conf.urls.static import static  # ✅ Needed for serving media during development
from .views import create_volunteer
from .views import list_volunteers
from .views import StewardshipRecordListView
from .views import StewardshipRecordUpdateView


app_name = 'church'

urlpatterns = [
    path('', views.home, name='homepage'),
    path('register-church/', views.register_church, name='register_church'),
    path('church-admin-login/', views.church_admin_login, name='church_admin_login'),
    path('church-admin-logout/', views.church_admin_logout, name='church_admin_logout'),
    path('church-admin-dashboard/', views.church_admin_dashboard, name='church_admin_dashboard'),
    path('upload-image/', views.upload_church_image, name='upload_church_image'),
    path('church-admin/volunteers/create/', create_volunteer, name='create_volunteer'),

    path('register-member/', MemberRegistrationView.as_view(), name='register_member'),
    path('member-login/', views.MemberLoginView.as_view(), name='member_login'),
    path('member-dashboard/', MemberDashboardView.as_view(), name='member_dashboard'),
    path('member-logout/', member_logout, name='member_logout'),
    path('member/profile/edit/', MemberProfileUpdateView.as_view(), name='edit_member_profile'),

   
path(
    'member-registration/success/',
    TemplateView.as_view(template_name='church/member_registration_success.html'),
    name='member_registration_success'
),



    # Each section
    path('church-admin/volunteers/', views.list_volunteers, name='list_volunteers'),
    path('volunteers/add/', views.create_volunteer, name='volunteer_add'),
    path('volunteers/<int:volunteer_id>/edit/', views.edit_volunteer, name='edit_volunteer'),
    path('volunteers/<int:volunteer_id>/delete/', views.delete_volunteer, name='delete_volunteer'),
    path('volunteer-login/', views.volunteer_login, name='volunteer_login'),

    


    path('church-events/', EventListView.as_view(), name='church_events'),
    path('church-events/add/', EventCreateView.as_view(), name='add_event'),
    path('church-events/<int:pk>/edit/', EventUpdateView.as_view(), name='edit_event'),
    path('church-events/<int:pk>/delete/', EventDeleteView.as_view(), name='delete_event'),    
    path('notifications/all/', all_notifications, name='all_notifications'), 
    path('notifications/check/', views.check_new_notifications, name='check_new_notifications'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notifications/mark-all-read/', mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    
    path('member-notifications/', views.member_notifications, name='member_notifications'),


    
    # Admin/Volunteer (Church Staff) Livestream Views
path('livestreams/', LiveStreamListView.as_view(), name='livestream_list'),
path('livestreams/add/', LiveStreamCreateView.as_view(), name='add_livestream'),
path('livestreams/<int:pk>/edit/', LiveStreamUpdateView.as_view(), name='livestream_edit'),
path('manage-livestreams/<int:pk>/delete/', LiveStreamDeleteView.as_view(), name='delete_livestream'),
path('livestreams/<int:pk>/delete/', LiveStreamDeleteView.as_view(), name='livestream_delete'),

# Member-facing livestream views
path('member-dashboard/livestreams/', MemberLiveStreamListView.as_view(), name='member_livestream_list'),
path('member/livestreams/<int:pk>/', MemberLiveStreamDetailView.as_view(), name='member_livestream_detail'),
path('member/watch-live/', WatchLiveView.as_view(), name='watch_live'),
path('member/logout/', member_logout, name='member_logout'),

# Chat posting
path('post-message/', PostMessageView.as_view(), name='post_message'),
path('chatrooms/', ChatRoomListView.as_view(), name='chatroom_list'),
path('chat/fetch-messages/', fetch_messages, name='fetch_messages'),
path('chatrooms/create/', ChatRoomCreateView.as_view(), name='create_chatroom'),
path('chatrooms/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom_detail'),
path('chatrooms/<int:pk>/edit/', ChatRoomUpdateView.as_view(), name='edit_chatroom'),
path('chatrooms/<int:pk>/delete/', ChatRoomDeleteView.as_view(), name='delete_chatroom'),
path('chat/edit/', views.edit_message, name='edit_message'),
path('chat/delete/', views.delete_message, name='delete_message'),

# Admin views
    path('church-announcements/', AdminAnnouncementListView.as_view(), name='church_announcement_list'),
    path('church-announcements/add/', AnnouncementCreateView.as_view(), name='add_announcement'),
    path('church-announcements/<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='edit_announcement'),
    path('church-announcements/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='delete_announcement'),
    path('member-announcement/<int:pk>/', MemberAnnouncementDetailView.as_view(), name='member_announcement_detail'),


    # Member views
    path('member-announcements/', MemberAnnouncementListView.as_view(), name='member_announcements'),
    path('member-announcements/<int:pk>/mark-read/', MarkAnnouncementReadView.as_view(), name='mark_announcement_read'),


    path('stewardship/', views.StewardshipRecordListView.as_view(), name='stewardship_list'),
    path('stewardship/add/', views.add_stewardship_record, name='add_stewardship_record'),
    path('stewardship/<int:pk>/edit/', views.StewardshipRecordUpdateView.as_view(), name='edit_stewardship_record'),
    path('stewardship/<int:pk>/delete/', views.StewardshipRecordDeleteView.as_view(), name='delete_stewardship_record'),
    path('stewardship/pdf/', views.generate_stewardship_pdf, name='generate_stewardship_pdf'),
    path('stewardship/export_excel/', views.export_stewardship_to_excel, name='export_stewardship_excel'),
    path("stewardship/export/pdf/filtered/", views.generate_filtered_pdf, name="generate_filtered_pdf"),
    path("stewardship/export/excel/filtered/", views.export_filtered_excel, name="export_filtered_excel"),
    path('stewardship/audit-log/', views.audit_log_view, name='stewardship_audit_logs'),


    # Soft delete a record
    path('stewardship/<int:pk>/trash/', views.soft_delete_stewardship_record, name='soft_delete_stewardship_record'),

    # Trash list view (only soft-deleted records)
    path('stewardship/trash/', views.stewardship_trash_list, name='stewardship_trash_list'),

    # Restore soft-deleted record
    path('stewardship/<int:pk>/restore/', views.restore_stewardship_record, name='restore_stewardship_record'),

    # Empty trash (permanent delete all soft-deleted records)
    path('stewardship/trash/empty/', views.empty_stewardship_trash, name='empty_stewardship_trash'),

      

  # Sunday income
path('income-receipt/new/', views.create_sunday_income_receipt, name='create_sunday_income_receipt'),
path('income-receipt/print/<int:receipt_id>/', views.print_sunday_income_receipt, name='print_sunday_income_receipt'),

    path('online-giving/', OnlineGivingView.as_view(), name='online_giving'),
    path('online-giving/receipt/<int:receipt_id>/', OnlineGivingReceiptView.as_view(), name='view_online_giving_receipt'),
    path('online-giving/receipt/<int:receipt_id>/pdf/', 
OnlineGivingReceiptView.as_view(), name='print_online_giving_receipt'),
    path('online-giving/receipt/<int:receipt_id>/', PrintOnlineGivingReceiptView.as_view(), name='print_online_giving_receipt'),
    path('online-giving/<int:pk>/delete/', DeleteOnlineGivingView.as_view(), name='delete_online_giving'),
   

path("income/create/", views.create_sunday_income_receipt, name="sunday_income_form"),

path('sunday-receipt/', views.sunday_income_receipt_list, name='sunday_income_receipt_list'),

path('sunday-receipt/<int:pk>/delete/', views.delete_sunday_income_receipt, name='delete_sunday_income_receipt'),

path('sunday-receipt/restore/<int:pk>/', views.restore_sunday_income_receipt, name='restore_sunday_income_receipt'),

path('sunday-income/receipts/pdf/', views.download_filtered_receipts_pdf, name='all_receipts_pdf'),

path('verify-receipt/<str:receipt_number>/', views.verify_receipt, name='verify_receipt'),

path('admin/regenerate-qr/<int:receipt_id>/', views.regenerate_qr_admin_view, name='regenerate_qr'),

path('sunday-receipt/trash/', views.trashed_sunday_income_receipts, name='trashed_sunday_income_list'),

path('receipts/<int:receipt_id>/permanent-delete/', views.permanently_delete_sunday_income_receipt, name='permanently_delete_receipt'),


path('online-giving/', OnlineGivingView.as_view(), name='online_giving'),
path(
        "church-admin/online-giving/",
        ChurchOnlineGivingView.as_view(),
        name="church_admin_online_giving",
    ),

path("sms-logs/", SMSLogListView.as_view(), name="sms_logs"),
path("sms-logs/<int:pk>/resend/", ResendSMSView.as_view(), name="resend_sms"),



path('stewardship/society_members_pdf/<str:society_name>/', generate_society_members_pdf, name='society_members_pdf'),


    path('church-admin-dashboard/reading-plans/', BibleReadingPlanListView.as_view(), name='bible_reading_list'),
    path('church-admin-dashboard/reading-plans/add/', BibleReadingPlanCreateView.as_view(), name='add_bible_reading'),
    path('church-admin-dashboard/reading-plans/<int:pk>/edit/', BibleReadingPlanUpdateView.as_view(), name='edit_bible_reading'),
    path('church-admin-dashboard/reading-plans/<int:pk>/delete/', BibleReadingPlanDeleteView.as_view(), name='delete_bible_reading'),


    path('member-dashboard/reading-today/', MemberBibleReadingTodayView.as_view(), name='member_reading_today'),
    path('member-dashboard/reading-archive/', MemberBibleReadingArchiveView.as_view(), name='member_reading_archive'),
    path('member-dashboard/reading-progress/', MemberReadingProgressView.as_view(), name='member_reading_progress'),
    path('member-dashboard/my-activity/', MemberActivityLogView.as_view(), name='member_activity_log'),

    path('mark-reading-done/', MarkReadingAsDoneView.as_view(), name='mark_reading_done'),


path('prayer-requests/', PrayerRequestListView.as_view(), name='prayer_request_list'),
    path('prayer-requests/add/', PrayerRequestCreateView.as_view(), name='add_prayer_request'),

path('volunteer/dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),


 path("make-payment/", PaymentInstructionsView.as_view(), name="make_payment"),



    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:staff_id>/edit/', views.edit_staff, name='edit_staff'),

    path('staff/<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),

    path('staff/payments/', staff_payment_list, name='staff_payment_list'),

    path('staff/payments/add/', views.add_staff_payment, name='add_staff_payment'),

    path('staff-salary-table/', views.StaffSalaryTableView.as_view(), name='staff_salary_table'),

    path('admin-dashboard/', views.church_admin_dashboard, name='church_admin_dashboard'),

   

path('edit-staff-payment/<int:pk>/', views.edit_staff_payment, name='edit_staff_payment'),
    path('delete-staff-payment/<int:pk>/', views.delete_staff_payment, name='delete_staff_payment'),
path('staff-salary-pdf/', views.staff_salary_pdf_view, name='staff_salary_pdf'),





# ▶︎ church/urls.py
path("member-chat/fetch/",  views.fetch_member_chat, name="member_chat_fetch"),
path("member-chat/post/",   views.post_member_chat,  name="member_chat_post"),
path("member-chat/delete/<int:pk>/", views.delete_member_chat_message, name="delete_member_chat_message"),


path("volunteer/member-chat/moderate/", MemberChatModerationListView.as_view(), name="volunteer_member_chat_moderation"),
path("member-chat/<int:pk>/delete/", delete_member_chat_message, name="delete_member_chat_message"),


    # Password reset
   path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# ✅ Only for development: Serve uploaded media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
