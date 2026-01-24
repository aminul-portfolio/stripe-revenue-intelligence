# scripts/job_first_closure_gates_head.ps1
# Clean proof capture for job-first closure gates, anchored to current HEAD.

[CmdletBinding()]
param(
  [string] $ProofPath = "docs/proof/job_2026-01-24_job_first_closure_gates_HEAD.txt"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$head = (git rev-parse HEAD).Trim()
$py = (python --version).Trim()

Remove-Item $ProofPath -ErrorAction SilentlyContinue

"=== Job-First Closure Gates (HEAD) — 2026-01-24 ===" | Out-File -Encoding utf8 $ProofPath
"PWD=$repoRoot" | Out-File -Encoding utf8 -Append $ProofPath
"PY=$py" | Out-File -Encoding utf8 -Append $ProofPath
"DJANGO_SETTINGS_MODULE=$env:DJANGO_SETTINGS_MODULE" | Out-File -Encoding utf8 -Append $ProofPath
"HEAD_COMMIT=$head" | Out-File -Encoding utf8 -Append $ProofPath
"" | Out-File -Encoding utf8 -Append $ProofPath

function Add-Section([string] $title) {
  "" | Out-File -Encoding utf8 -Append $ProofPath
  "## $title" | Out-File -Encoding utf8 -Append $ProofPath
}

# 1) check
Add-Section "python manage.py check"
& powershell -ExecutionPolicy Bypass -File "scripts/_capture_cmd.ps1" `
  -Command "python manage.py check" -OutFile $ProofPath
$checkExit = $LASTEXITCODE
"" | Out-File -Encoding utf8 -Append $ProofPath
"CHECK_EXITCODE=$checkExit" | Out-File -Encoding utf8 -Append $ProofPath

# 2) migrations check
Add-Section "python manage.py makemigrations --check --dry-run"
& powershell -ExecutionPolicy Bypass -File "scripts/_capture_cmd.ps1" `
  -Command "python manage.py makemigrations --check --dry-run" -OutFile $ProofPath
$migExit = $LASTEXITCODE
"" | Out-File -Encoding utf8 -Append $ProofPath
"MIGRATIONS_EXITCODE=$migExit" | Out-File -Encoding utf8 -Append $ProofPath

# 3) tests
Add-Section "python manage.py test"
& powershell -ExecutionPolicy Bypass -File "scripts/_capture_cmd.ps1" `
  -Command "python manage.py test" -OutFile $ProofPath
$testExit = $LASTEXITCODE
"" | Out-File -Encoding utf8 -Append $ProofPath
"TEST_EXITCODE=$testExit" | Out-File -Encoding utf8 -Append $ProofPath

# 4) run_checks
Add-Section "python manage.py run_checks --fail-on-issues"
& powershell -ExecutionPolicy Bypass -File "scripts/_capture_cmd.ps1" `
  -Command "python manage.py run_checks --fail-on-issues" -OutFile $ProofPath
$rcExit = $LASTEXITCODE
"" | Out-File -Encoding utf8 -Append $ProofPath
"RUN_CHECKS_EXITCODE=$rcExit" | Out-File -Encoding utf8 -Append $ProofPath

# Overall result
$overall = 0
if ($checkExit -ne 0 -or $migExit -ne 0 -or $testExit -ne 0 -or $rcExit -ne 0) { $overall = 1 }
exit $overall
