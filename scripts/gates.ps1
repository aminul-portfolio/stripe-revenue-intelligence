param(
  [string]$ProofPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProofPath)) {
  $date = Get-Date -Format "yyyy-MM-dd"
  $ProofPath = "docs/proof/m3_${date}_full_gates.txt"
}

New-Item -ItemType Directory -Force -Path (Split-Path $ProofPath) | Out-Null

function Proof-WriteLine([string]$Line) {
  $Line | Out-File -FilePath $ProofPath -Append -Encoding utf8
}

function Invoke-Gate([string]$Title, [string]$Cmd) {
  Write-Host ""
  Write-Host ("== " + $Title + " ==")

  Proof-WriteLine ""
  Proof-WriteLine ("== " + $Title + " ==")

  # Stream output to proof as the command runs (no buffering, no truncation)
  $cmdLine = "$Cmd >> `"$ProofPath`" 2>&1"
  cmd /c $cmdLine

  if ($LASTEXITCODE -ne 0) {
    Proof-WriteLine ("EXITCODE=" + $LASTEXITCODE)
    throw ("Gate failed: " + $Title + " (exit=" + $LASTEXITCODE + ")")
  }
}

# Fresh header (overwrite existing proof file)
"== PureLaka Gates ==" | Out-File -FilePath $ProofPath -Encoding utf8
("Timestamp: " + (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")) | Out-File -FilePath $ProofPath -Append -Encoding utf8
("PWD: " + (Get-Location).Path) | Out-File -FilePath $ProofPath -Append -Encoding utf8
"" | Out-File -FilePath $ProofPath -Append -Encoding utf8

Write-Host "== PureLaka Gates =="

Invoke-Gate "Django check" "python manage.py check"
Invoke-Gate "Tests" "python manage.py test"
Invoke-Gate "Monitoring checks" "python manage.py run_checks --fail-on-issues"
Invoke-Gate "Migrations check" "python manage.py makemigrations --check --dry-run"
Invoke-Gate "Ruff lint" "ruff check ."
Invoke-Gate "Ruff format check" "ruff format --check ."
Invoke-Gate "pip-audit" "pip-audit -r requirements.txt"

Write-Host ""
Write-Host "== ALL GATES PASSED =="

Proof-WriteLine ""
Proof-WriteLine "== ALL GATES PASSED =="

Write-Host ("Proof written: " + $ProofPath)
