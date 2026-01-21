from pathlib import Path
import re

p = Path("docs/STATUS.md")
t = p.read_text(encoding="utf-8")

clean = "docs/proof/m3_2026-01-21_full_gates_clean.txt"

# Preserve file newline style
nl = "\r\n" if "\r\n" in t else "\n"

# 1) Replace any old consolidated-gates proof references (20/21, clean/non-clean) with the clean proof
t = re.sub(
    r"docs/proof/m3_2026-01-(?:20|21)_full_gates(?:_clean)?\.txt",
    clean,
    t,
)

# 2) Ensure the chronological bullet is canonical (date must match the file)
canonical_note = f"* 2026-01-21: Consolidated M3 gates proof captured as a buyer-ready snapshot (`{clean}`)."

# Replace any existing "Consolidated M3 gates proof captured..." bullet to canonical
t2 = re.sub(
    r"^\*\s+2026-01-(?:20|21):\s+Consolidated M3 gates proof captured as a buyer-ready snapshot \(`docs/proof/[^`]+`\)\.\s*$",
    canonical_note,
    t,
    flags=re.M,
)

t = t2

# If canonical note still missing, insert it after the "Contracts & Proof Index..." bullet in Notes (chronological)
if canonical_note not in t:
    m = re.search(
        r"^\*\s+2026-01-20:\s+Contracts & Proof Index added as the buyer due-diligence entry point \(`docs/CONTRACTS_AND_PROOFS\.md`\)\.\s*$",
        t,
        flags=re.M,
    )
    if m:
        insert_pos = m.end()
        t = t[:insert_pos] + nl + canonical_note + t[insert_pos:]
    else:
        # As a fallback, insert before "## Evidence (proof artifacts)"
        m2 = re.search(r"^## Evidence \(proof artifacts\)\s*$", t, flags=re.M)
        if m2:
            insert_pos = m2.start()
            t = t[:insert_pos] + canonical_note + nl + nl + t[insert_pos:]

# 3) Ensure authoritative section contains the clean proof bullet
auth_header_re = re.compile(r"^Consolidated M3 gates proof \(authoritative\):\s*$", re.M)
m = auth_header_re.search(t)
if m:
    # Find the block starting right after the header line
    header_end = m.end()
    # Ensure there's a blank line after header
    # Insert the bullet immediately after the header + blank line
    # First, normalize any old bullet in the immediate lines that follow
    # Replace any existing bullet in that section that points to older consolidated proof
    t = re.sub(
        r"(^Consolidated M3 gates proof \(authoritative\):\s*\r?\n\s*\r?\n)\*\s+`docs/proof/m3_2026-01-(?:20|21)_full_gates(?:_clean)?\.txt`\s*\r?\n",
        r"\1* `" + clean + r"`" + nl,
        t,
        flags=re.M,
    )

    # If still missing anywhere, insert bullet right after header (after blank line)
    if f"* `{clean}`" not in t:
        t = re.sub(
            r"(^Consolidated M3 gates proof \(authoritative\):\s*\r?\n\s*\r?\n)",
            r"\1* `" + clean + r"`" + nl,
            t,
            count=1,
            flags=re.M,
        )

# Write back
p.write_text(t, encoding="utf-8")

# Print check flags
ok_date = canonical_note in t
ok_auth = f"* `{clean}`" in t
print("DATE_LINE_OK=", ok_date)
print("AUTHORITATIVE_OK=", ok_auth)
