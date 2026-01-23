from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


REQUIRED_DOCS = [
    Path("docs/STATUS.md"),
    Path("docs/CONTRACTS_AND_PROOFS.md"),
]

PROOF_DIR = Path("docs/proof")


class Command(BaseCommand):
    help = (
        "Verify docs index integrity: required docs exist, proof files referenced exist, "
        "and buyer entry points are present."
    )

    def handle(self, *args, **options) -> None:
        repo_root = Path(".").resolve()

        missing_docs = [p for p in REQUIRED_DOCS if not p.exists()]
        if missing_docs:
            raise CommandError(
                f"Missing required docs: {', '.join(str(p) for p in missing_docs)}"
            )

        if not PROOF_DIR.exists():
            raise CommandError("Missing docs/proof/ directory")

        # Read docs
        status_text = REQUIRED_DOCS[0].read_text(encoding="utf-8")
        contracts_text = REQUIRED_DOCS[1].read_text(encoding="utf-8")

        # Buyer entry point sanity
        if "Buyer entry point" not in contracts_text:
            raise CommandError(
                "docs/CONTRACTS_AND_PROOFS.md missing 'Buyer entry point' section"
            )

        # Collect referenced proof paths in both docs.
        referenced = sorted(
            set(
                _extract_proof_paths(status_text) + _extract_proof_paths(contracts_text)
            )
        )

        if not referenced:
            raise CommandError(
                "No docs/proof references found in STATUS.md or CONTRACTS_AND_PROOFS.md"
            )

        missing_proofs = [p for p in referenced if not p.exists()]
        if missing_proofs:
            msg = "Missing proof files referenced by docs:\n" + "\n".join(
                f"- {p.as_posix()}" for p in missing_proofs
            )
            raise CommandError(msg)

        self.stdout.write("== DOCS INDEX GATES ==")
        self.stdout.write(f"Repo: {repo_root}")
        self.stdout.write(f"Proof references found: {len(referenced)}")
        self.stdout.write("All referenced proof files exist.")
        self.stdout.write("== ALL DOCS INDEX GATES PASSED ==")


def _extract_proof_paths(text: str) -> list[Path]:
    out: list[Path] = []
    for line in text.splitlines():
        line = line.strip()
        # Look for the standard token pattern you use everywhere:
        # docs/proof/<filename>
        if "docs/proof/" in line:
            # Extract all occurrences in the line (can be multiple).
            parts = line.split("docs/proof/")
            for tail in parts[1:]:
                # tail starts with filename then maybe punctuation/backticks/paren.
                fname = ""
                for ch in tail:
                    if ch.isalnum() or ch in ("_", "-", ".", "/"):
                        fname += ch
                    else:
                        break
                if fname:
                    out.append(Path("docs/proof") / fname)
    return out
