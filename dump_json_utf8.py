import os
import django
from django.core.management import call_command

# ✅ Point to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_management_system.settings")

django.setup()

with open("backups/db_dump.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", stdout=f, indent=2)
