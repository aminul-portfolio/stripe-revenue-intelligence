import re
from pathlib import Path

p = Path("docs/STATUS.md")
text = p.read_text(encoding="utf-8")

if "m3_deploy_gate_2026-01-21.txt" in text:
    print("No change needed: already present.")
else:
    pat = re.compile(r"(^\*\s+.*docs/proof/m3_2026-01-20_full_gates\.txt.*\r?\n)", re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit("ERROR: could not find the m3_2026-01-20_full_gates bullet line")

    nl = "\r\n" if m.group(1).endswith("\r\n") else "\n"
    new = pat.sub(
        lambda _m: _m.group(1)
        + f"* `scripts/gates.ps1`{nl}"
        + f"* `scripts/deploy_gate.ps1`{nl}"
        + f"* `docs/proof/m3_deploy_gate_2026-01-21.txt`{nl}",
        text,
        count=1,
    )
    p.write_text(new, encoding="utf-8")
    print("Inserted after m3_2026-01-20_full_gates bullet.")
