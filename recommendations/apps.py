import sys
from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recommendations"

    def ready(self):
        # Don't warm up during migrations / collectstatic / shell.
        skip = {"migrate", "makemigrations", "collectstatic", "shell", "test"}
        if any(cmd in sys.argv for cmd in skip):
            return

        from recommender.engine import HybridRecommender

        try:
            HybridRecommender.get()
        except FileNotFoundError:
            # Artifacts not built yet — the first request will fail loudly.
            pass