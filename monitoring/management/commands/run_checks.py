from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.models import Count

from monitoring.models import DataQualityIssue
from monitoring.services.run_all import run_all_checks


class Command(BaseCommand):
    help = "Run monitoring checks and print a concise operational report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-issues",
            action="store_true",
            help="Exit with error code if any OPEN issues exist (useful for CI).",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=10,
            help="Show up to N latest OPEN issues as examples (default: 10).",
        )

        # ✅ NEW
        parser.add_argument(
            "--refresh-snapshots",
            action="store_true",
            help="Rebuild analytics snapshots before running checks (prevents stale snapshot mismatches).",
        )
        parser.add_argument(
            "--snapshots-days",
            type=int,
            default=90,
            help="How many days to rebuild when refreshing snapshots (default: 90).",
        )

    def handle(self, *args, **options):
        # ✅ NEW: refresh snapshots before running checks
        # - If you're using --fail-on-issues (CI), you almost always want fresh snapshots.
        should_refresh = bool(options["refresh_snapshots"] or options["fail_on_issues"])
        if should_refresh:
            days = max(1, int(options["snapshots_days"] or 90))
            # keep output quiet; your command already prints a report
            call_command("build_analytics_snapshots", days=days, verbosity=0)

        run_all_checks()

        total = DataQualityIssue.objects.count()
        open_count = DataQualityIssue.objects.filter(status="open").count()
        resolved_count = DataQualityIssue.objects.filter(status="resolved").count()

        breakdown = (
            DataQualityIssue.objects.values("issue_type", "status")
            .annotate(n=Count("id"))
            .order_by("-n")
        )

        # Header line
        if open_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Issues: {open_count} (open={open_count}, resolved={resolved_count})"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Issues: {open_count} (open={open_count}, resolved={resolved_count})"
                )
            )

        if total:
            self.stdout.write("\nBreakdown:")
            for row in breakdown:
                self.stdout.write(
                    f" - {row['issue_type']} / {row['status']}: {row['n']}"
                )

            top_n = max(0, int(options["top"]))
            if top_n:
                self.stdout.write(f"\nLatest {top_n} open issues:")

                qs = DataQualityIssue.objects.filter(status="open").order_by(
                    "-created_at"
                )[:top_n]
                if not qs:
                    self.stdout.write(" - (none open)")
                else:
                    for i in qs:
                        desc = (i.description or "").replace("\n", " ").strip()
                        if len(desc) > 120:
                            desc = desc[:117] + "..."
                        self.stdout.write(
                            f" - #{i.id} [{i.status}] {i.issue_type} {i.reference_id} :: {desc}"
                        )

        if options["fail_on_issues"] and open_count > 0:
            raise CommandError(f"Monitoring failed: {open_count} open issue(s).")
