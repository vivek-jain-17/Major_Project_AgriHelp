from django.contrib import admin
from .models import Scheme

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "scheme_level", "slug", "scraped_at")
    list_filter = ("state", "scheme_level", "eligibility_disability", "eligibility_bpl")
    search_fields = ("name", "description", "scheme_text")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)
    
    # We group the fields in the admin for easier reading
    fieldsets = (
        ("Identity", {"fields": ("id", "slug", "name", "scheme_level", "state")}),
        ("Agency", {"fields": ("ministry", "department")}),
        ("Content", {"fields": ("description", "benefits", "eligibility_text", "application_process", "documents_required")}),
        ("Categorization", {"fields": ("categories", "beneficiary_types", "eligible_states")}),
        ("Structured Eligibility", {"fields": (
            "eligibility_age_min", "eligibility_age_max", "eligibility_gender", 
            "eligibility_caste", "eligibility_income_max", "eligibility_residence", 
            "eligibility_disability", "eligibility_bpl"
        )}),
        ("Links & Metadata", {"fields": ("apply_url", "official_url", "scraped_at", "scheme_text", "created_at", "updated_at")}),
    )