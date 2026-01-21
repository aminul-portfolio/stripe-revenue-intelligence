from pathlib import Path
import re

p = Path("docs/CONTRACTS_AND_PROOFS.md")
t = p.read_text(encoding="utf-8")

# If there's an M3 section, append missing items near the existing M3 proof bullets.
# We anchor on the first existing M3 proof bullet.
anchor = "- `docs/proof/m3_export_contract_tests_2026-01-20.txt`"

add_block = """- `docs/proof/m3_export_contract_test_verbose_2026-01-20.txt`
- `docs/proof/m3_kpi_contract_alignment_2026-01-20.txt`
- `docs/proof/m3_kpi_inventory_2026-01-20.txt`
- `docs/proof/m3_2026-01-21_full_gates_clean.txt`
- `docs/proof/m3_deploy_gate_2026-01-21.txt`
- `scripts/gates.ps1`
- `scripts/deploy_gate.ps1`"""

if anchor not in t:
    raise SystemExit("ERROR: Could not find the existing M3 anchor line in docs/CONTRACTS_AND_PROOFS.md")

# Insert missing lines right after the anchor line, but only if they are not already present.
lines_to_add = [ln for ln in add_block.splitlines() if ln.strip() and ln not in t]

if not lines_to_add:
    print("No change needed: all M3 proof/tooling lines already present.")
else:
    t = t.replace(anchor, anchor + "\n" + "\n".join(lines_to_add))
    p.write_text(t, encoding="utf-8")
    print("Updated docs/CONTRACTS_AND_PROOFS.md (added missing M3 proof/tooling lines).")
