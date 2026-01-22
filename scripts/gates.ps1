param(
  [string]$ProofPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProofPath)) {
  $date = Get-Date -Format "yyyy-MM-dd"
  $ProofPath = "docs/proof/m3_${date}_full_gates_clean.txt"
}

New-Item -ItemType Directory -Force -Path (Split-Path $ProofPath) | Out-Null

# UTF-8 WITHOUT BOM (buyer-friendly, diff-friendly proof artifacts)
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Proof-WriteLine([string]$Line) {
  $sw = New-Object System.IO.StreamWriter($ProofPath, $true, $Utf8NoBom)
  try {
    $sw.WriteLine($Line)
  } finally {
    $sw.Dispose()
  }
}

function Proof-Write([string]$Text) {
  $sw = New-Object System.IO.StreamWriter($ProofPath, $true, $Utf8NoBom)
  try {
    $sw.Write($Text)
  } finally {
    $sw.Dispose()
  }
}

function Proof-ResetFile() {
  $sw = New-Object System.IO.StreamWriter($ProofPath, $false, $Utf8NoBom)
  try {
    # create/overwrite file with no BOM
  } finally {
    $sw.Dispose()
  }
}

function Invoke-Gate([string]$Title, [string]$Cmd) {
  Write-Host ""
  Write-Host ("== " + $Title + " ==")

  Proof-WriteLine ""
  Proof-WriteLine ("== " + $Title + " ==")

  # Append live output to proof while running (cmd handles redirection reliably)
  $cmdLine = "$Cmd >> `"$ProofPath`" 2>&1"
  cmd /c $cmdLine

  if ($LASTEXITCODE -ne 0) {
    Proof-WriteLine ("EXITCODE=" + $LASTEXITCODE)
    throw ("Gate failed: " + $Title + " (exit=" + $LASTEXITCODE + ")")
  }
}

# Fresh header (overwrite existing proof file; no BOM)
Proof-ResetFile
Proof-WriteLine "== PureLaka Gates =="
Proof-WriteLine ("Timestamp: " + (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))
Proof-WriteLine ("PWD: " + (Get-Location).Path)
Proof-WriteLine ""

Write-Host "== PureLaka Gates =="

Invoke-Gate "Django check" "python manage.py check"
Invoke-Gate "Tests" "python manage.py test --noinput"
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
