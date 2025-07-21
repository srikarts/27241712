from django.db import models
from django.utils import timezone
import string, random
from datetime import timedelta

class ShortURL(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    validity_period = models.DurationField(default=timedelta(days=30)) 
    
    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        super().save(*args, **kwargs)

class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='clicks')
    timestamp = models.DateTimeField(default=timezone.now)
    referrer = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # optional
