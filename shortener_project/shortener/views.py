from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import ShortURL
from datetime import timedelta
import random
import string
from .models import ShortURL, ClickEvent


def redirect_to_original(request, code):
    obj = get_object_or_404(ShortURL, short_code=code)
    return redirect(obj.original_url)


def generate_unique_shortcode(length=6):
    while True:
        shortcode = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not ShortURL.objects.filter(short_code=shortcode).exists():
            return shortcode

@csrf_exempt
def create_short_url(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            original_url = data.get("url")
            validity = data.get("validity", 30)
            shortcode = data.get("shortcode")

            if not original_url:
                return JsonResponse({"error": "URL is required"}, status=400)

            # If shortcode is provided, check for uniqueness
            if shortcode:
                if ShortURL.objects.filter(short_code=shortcode).exists():
                    return JsonResponse({"error": "Shortcode already taken"}, status=400)
            else:
                shortcode = generate_unique_shortcode()

            obj = ShortURL.objects.create(
                original_url=original_url,
                short_code=shortcode
            )

            expiry_time = obj.created_at + timedelta(minutes=int(validity))
            return JsonResponse({
                "shortLink": request.build_absolute_uri(f'/{obj.short_code}'),
                "expiry": expiry_time
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def get_url_statistics(request, shortcode):
    # Fetch the ShortURL object by shortcode
    short_url = get_object_or_404(ShortURL, short_code=shortcode)

    # Gather all clicks associated with this short URL
    click_events = ClickEvent.objects.filter(short_url=short_url)

    # Construct click detail list
    click_details = []
    for click in click_events:
        click_details.append({
            "timestamp": click.timestamp,
            "referrer": click.referrer,
            "location": click.location  # assuming you store coarse location
        })

    # Build response
    stats = {
        "original_url": short_url.original_url,
        "short_code": short_url.short_code,
        "created_at": short_url.created_at,
        "expiry_date": short_url.created_at + short_url.validity_period,  # if you're storing validity
        "total_clicks": click_events.count(),
        "click_data": click_details
    }

    return JsonResponse(stats, safe=False)
