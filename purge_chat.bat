@echo off
cd /d "C:\Users\USER\Church Management System"
call venz\Scripts\activate
python manage.py purge_member_chat
