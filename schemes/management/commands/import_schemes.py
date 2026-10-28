import csv
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from schemes.models import Scheme

class Command(BaseCommand):
    help = "Imports schemes from agriculture_schemes_initial.csv safely"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", 
            type=str, 
            default="agriculture_schemes_initial.csv", 
            help="Path to CSV file (relative to project root)"
        )

    def handle(self, *args, **options):
        file_path = Path(settings.BASE_DIR) / options["file"]
        
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        inserted = 0
        updated = 0
        errors = 0

        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2): # Start at 2 because row 1 is headers
                try:
                    slug = row["slug"].strip()
                    if not slug:
                        raise ValueError("Missing slug")

                    # 1. Safe JSON parsing for lists (e.g. '["Puducherry"]' or 'Agriculture,Social')
                    def parse_list(val):
                        if not val or val.strip() == "":
                            return []
                        val = val.strip()
                        # If it looks like a JSON array string
                        if val.startswith("[") and val.endswith("]"):
                            try:
                                parsed = json.loads(val.replace("'", '"'))
                                return [str(x).strip() for x in parsed if x]
                            except json.JSONDecodeError:
                                pass
                        # Otherwise, assume comma separated
                        return [x.strip() for x in val.split(",") if x.strip()]

                    # 2. Safe Booleans ("False" -> False, "True" -> True, "" -> None)
                    def parse_bool(val):
                        if not val or val.strip() == "": return None
                        return val.strip().lower() == "true"

                    # 3. Safe Decimals ("" -> None, NEVER 0)
                    def parse_decimal(val, max_digits=None):
                        if not val or val.strip() == "": return None
                        try:
                            return Decimal(val.strip())
                        except InvalidOperation:
                            return None

                    # 4. Safe Datetime
                    def parse_dt(val):
                        if not val or val.strip() == "": return None
                        return parse_datetime(val.strip())

                    # Map CSV to Model fields
                    defaults = {
                        "name": row.get("name", "").strip(),
                        "description": row.get("description", "").strip(),
                        "ministry": row.get("ministry", "").strip() or None,
                        "department": row.get("department", "").strip() or None,
                        "state": row.get("state", "").strip(),
                        "categories": parse_list(row.get("category")),
                        "beneficiary_types": parse_list(row.get("beneficiary_type")),
                        "benefits": row.get("benefits", "").strip(),
                        "eligibility_text": row.get("eligibility_text", "").strip(),
                        "application_process": row.get("application_process", "").strip(),
                        "documents_required": row.get("documents_required", "").strip(),
                        "apply_url": row.get("apply_url", "").strip() or None,
                        "official_url": row.get("official_url", "").strip() or None,
                        "eligibility_age_min": parse_decimal(row.get("eligibility_age_min")),
                        "eligibility_age_max": parse_decimal(row.get("eligibility_age_max")),
                        "eligibility_gender": row.get("eligibility_gender", "").strip(),
                        "eligibility_caste": parse_list(row.get("eligibility_caste")),
                        "eligibility_income_max": parse_decimal(row.get("eligibility_income_max")),
                        "eligibility_residence": row.get("eligibility_residence", "").strip(),
                        "eligible_states": parse_list(row.get("eligibility_state")),
                        "eligibility_disability": parse_bool(row.get("eligibility_disability")),
                        "eligibility_bpl": parse_bool(row.get("eligibility_bpl")),
                        "scraped_at": parse_dt(row.get("scraped_at")),
                        "scheme_text": row.get("scheme_text", "").strip(),
                    }

                    # Determine Scheme Level based on state
                    state_lower = defaults["state"].lower()
                    if "central" in state_lower or "all" in state_lower:
                        defaults["scheme_level"] = Scheme.SchemeLevel.CENTRAL
                    elif defaults["state"]:
                        defaults["scheme_level"] = Scheme.SchemeLevel.STATE
                    else:
                        defaults["scheme_level"] = Scheme.SchemeLevel.OTHER

                    # Upsert (Update if exists, Insert if not)
                    obj, created = Scheme.objects.update_or_create(
                        slug=slug,
                        defaults=defaults
                    )

                    if created:
                        inserted += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f"Row {row_num} error: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nImport complete.\n"
            f"Inserted: {inserted}\n"
            f"Updated:  {updated}\n"
            f"Errors:   {errors}\n"
        ))