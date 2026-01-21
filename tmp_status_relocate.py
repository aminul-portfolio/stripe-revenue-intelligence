from pathlib import Path

p = Path("docs/STATUS.md")
text = p.read_text(encoding="utf-8")

items = [
    "* `scripts/gates.ps1`",
    "* `scripts/deploy_gate.ps1`",
    "* `docs/proof/m3_deploy_gate_2026-01-21.txt`",
]

# Remove them wherever they currently are
lines = [ln for ln in text.splitlines() if ln.strip() not in {i.strip() for i in items}]

text2 = "\n".join(lines) + "\n"

anchor = "Consolidated M3 gates proof (authoritative):\n\n* `docs/proof/m3_2026-01-20_full_gates.txt`\n"
if anchor not in text2:
    raise SystemExit("ERROR: Could not find the M3 proof pack consolidated gates anchor block.")

insertion = anchor + "\n".join(items) + "\n"
text3 = text2.replace(anchor, insertion)

p.write_text(text3, encoding="utf-8")
print("Relocated script/proof bullets to M3 proof pack section.")
