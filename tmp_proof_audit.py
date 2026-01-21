from pathlib import Path

files = ["docs/CONTRACTS_AND_PROOFS.md", "docs/STATUS.md"]
needles = ("docs/proof/m3_", "m3_2026-01", "scripts/gates.ps1", "scripts/deploy_gate.ps1")

for f in files:
    p = Path(f)
    print(f"\n=== {f} ===")
    t = p.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(t, 1):
        if any(n in line for n in needles):
            print(f"{i:04d}: {line}")
