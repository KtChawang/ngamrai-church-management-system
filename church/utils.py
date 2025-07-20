from datetime import timedelta
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
import requests
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io


api_key = settings.FAST2SMS_API_KEY



def render_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("PDF generation error", status=500)


def get_user_church(user):
    """
    Safely get the church for either a member or a church admin.
    Returns None if user has no associated profile.
    """
    if hasattr(user, 'churchadminprofile'):
        return user.churchadminprofile.church
    elif hasattr(user, 'member'):
        return user.member.church
    return None


# ✅ Real Fast2SMS Integration
def send_sms(phone_number, message):
    url = settings.FAST2SMS_API_URL
    payload = {
        "route": settings.FAST2SMS_ROUTE,            # e.g., "v3"
        "sender_id": settings.FAST2SMS_SENDER_ID,    # e.g., "FSTSMS"
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": phone_number,
    }

    headers = {
        'authorization': settings.FAST2SMS_API_KEY,
        'Content-Type': "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        json_resp = response.json()
        if json_resp.get("return") is True:
            print(f"✅ SMS sent to {phone_number}")
        else:
            print(f"⚠️ SMS failed: {json_resp}")
        return json_resp
    except requests.RequestException as e:
        print(f"❌ SMS error: {e}")
        return None


def get_scripture_passage(reference):
    """
    Fetch Bible verses for any reference using Bible API.
    """
    try:
        response = requests.get(f"https://bible-api.com/{reference}")
        response.raise_for_status()
        data = response.json()

        verses = []
        for verse in data.get("verses", []):
            verses.append({
                "verse": f"{verse['verse']}",
                "text": verse["text"].strip()
            })

        return {
            "reference": data.get("reference", reference),
            "verses": verses,
            "commentary": "Auto-fetched from Bible-API.com"
        }

    except Exception as e:
        print(f"❌ Failed to fetch scripture: {e}")
        return {
            "reference": reference,
            "verses": [],
            "commentary": "Could not fetch verse. Please check your reference."
        }



User = get_user_model()

def get_online_members():
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    for session in sessions:
        data = session.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            uid_list.append(uid)

    return User.objects.filter(id__in=uid_list, is_member=True)


