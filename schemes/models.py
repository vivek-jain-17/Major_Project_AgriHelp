import uuid
from django.db import models
from django.utils.text import slugify

class Scheme(models.Model):
    class SchemeLevel(models.TextChoices):
        CENTRAL = "CENTRAL", "Central"
        STATE = "STATE", "State"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core Identifiers
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    name = models.CharField(max_length=300)
    
    # Descriptions & Benefits (Rich Text)
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    eligibility_text = models.TextField(blank=True)
    application_process = models.TextField(blank=True)
    documents_required = models.TextField(blank=True)
    
    # Agency Details
    ministry = models.CharField(max_length=250, blank=True, null=True)
    department = models.CharField(max_length=250, blank=True, null=True)
    scheme_level = models.CharField(max_length=20, choices=SchemeLevel.choices, default=SchemeLevel.OTHER)
    
    # Geographic Scope
    state = models.CharField(max_length=100, blank=True) # The state that owns/issued the scheme
    # We store lists (categories, beneficiaries, eligible states) as JSONB arrays.
    categories = models.JSONField(default=list, blank=True)
    beneficiary_types = models.JSONField(default=list, blank=True)
    eligible_states = models.JSONField(default=list, blank=True)
    
    # URLs
    apply_url = models.URLField(max_length=1000, blank=True, null=True)
    official_url = models.URLField(max_length=1000, blank=True, null=True)
    
    # Structured Eligibility Data (Null = Unknown, NEVER 0 or False)
    eligibility_age_min = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    eligibility_age_max = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    eligibility_gender = models.CharField(max_length=50, blank=True)
    eligibility_caste = models.JSONField(default=list, blank=True)
    eligibility_income_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    eligibility_residence = models.CharField(max_length=50, blank=True)
    eligibility_disability = models.BooleanField(null=True, blank=True)
    eligibility_bpl = models.BooleanField(null=True, blank=True)
    
    # Metadata
    scraped_at = models.DateTimeField(null=True, blank=True)
    scheme_text = models.TextField(blank=True) # Removed db_index=True) # Used for AI/Retrieval later
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["state", "scheme_level"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)