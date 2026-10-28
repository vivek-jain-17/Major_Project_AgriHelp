import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class UserRole(models.TextChoices):
    FARMER = "FARMER", "Farmer"
    ADMIN = "ADMIN", "Administrator"
    RESEARCHER = "RESEARCHER", "Researcher"

class User(AbstractUser):
    """
    Email-based custom user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150, unique=True, blank=True, null=True,
        help_text="Optional. Shown in admin if set."
    )
    email = models.EmailField(
        "email address", unique=True,
        help_text="Required. Used as the login identifier."
    )
    role = models.CharField(
        max_length=30, choices=UserRole.choices, default=UserRole.FARMER
    )
    preferred_language = models.CharField(
        max_length=10, default="en",
        help_text="ISO 639-1 language code, e.g. en, hi, mr."
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email