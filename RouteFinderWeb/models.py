from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_street = models.TextField(blank=True, help_text="Street address and City")
    home_zip = models.CharField(max_length=10, blank=True)
    home_state = models.CharField(max_length=2, blank=True)
    default_stop_mins = models.IntegerField(default=15, help_text="Default minutes spent at each individual garage sale.")
    
    # AI Discovery Preferences
    looking_for = models.TextField(blank=True, help_text="Comma-separated items you are looking for (e.g. 'Vintage Pyrex, Gameboy')")

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class SavedRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_routes')
    name = models.TextField(default="Weekend Route")
    start_time_str = models.TextField(default="08:00")
    stop_mins = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class RouteStop(models.Model):
    route = models.ForeignKey(SavedRoute, on_delete=models.CASCADE, related_name='stops')
    order_index = models.IntegerField()
    address = models.CharField(max_length=500, db_index=True)
    drive_time_str = models.TextField(blank=True)
    arrival_time = models.TextField(blank=True)
    departure_time = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order_index']

class AddressRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address_ratings')
    address = models.CharField(max_length=500, db_index=True)
    
    RATING_CHOICES = [
        ('bust', 'Bust'),
        ('great', 'Great Find'),
        ('neutral', 'Neutral')
    ]
    rating = models.CharField(max_length=10, choices=RATING_CHOICES, default='neutral')
    notes = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'address')
        
    def __str__(self):
        return f"{self.address} ({self.rating})"
class ScoutIntel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scout_intel')
    data = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Scout Intel for {self.user.username}"
