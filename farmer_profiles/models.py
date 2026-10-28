import uuid
from django.db import models
from django.conf import settings

class FarmerProfile(models.Model):
    class LandOwnership(models.TextChoices):
        OWNED = "OWNED", "Owned"
        LEASED = "LEASED", "Leased"
        SHARED = "SHARED", "Shared"

    class FarmerCategory(models.TextChoices):
        GENERAL = "GENERAL", "General"
        OBC = "OBC", "Other Backward Class"
        SC = "SC", "Scheduled Caste"
        ST = "ST", "Scheduled Tribe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    
    landholding_acres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    land_ownership = models.CharField(max_length=20, choices=LandOwnership.choices, blank=True)
    farmer_category = models.CharField(max_length=20, choices=FarmerCategory.choices, blank=True)
    
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

class FarmerCrop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="crops")
    crop_name = models.CharField(max_length=100)
    area_acres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.crop_name} ({self.area_acres} acres)"