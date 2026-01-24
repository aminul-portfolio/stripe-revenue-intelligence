# scripts/job_first_deploy_gate_head.ps1
# Clean deploy gate proof capture (prod-like), anchored to current HEAD.

[CmdletBinding()]
param(
  [string] $ProofPath = "docs/proof/job_2026-01-24_job_first_deploy_gate_HEAD.txt"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$head = (git rev-parse HEAD).Trim()
$py = (python --version).Trim()

Remove-Item $ProofPath -ErrorAction SilentlyContinue

"=== Deploy Gate Proof (prod-like) — 2026-01-24 ===" | Out-File -Encoding utf8 $ProofPath
"PWD=$repoRoot" | Out-File -Encoding utf8 -Append $ProofPath
"PY=$py" | Out-File -Encoding utf8 -Append $ProofPath
"BEFORE_DJANGO_SETTINGS_MODULE=$env:DJANGO_SETTINGS_MODULE" | Out-File -Encoding utf8 -Append $ProofPath
"HEAD_COMMIT=$head" | Out-File -Encoding utf8 -Append $ProofPath
"" | Out-File -Encoding utf8 -Append $ProofPath

"## python manage.py check --deploy (prod-like)" | Out-File -Encoding utf8 -Append $ProofPath

& powershell -ExecutionPolicy Bypass -File "scripts/_capture_cmd.ps1" `
  -Command "python manage.py check --deploy" `
  -OutFile $ProofPath `
  -Env @{ DJANGO_SETTINGS_MODULE = "purelaka.settings_prod" }

$deployExit = $LASTEXITCODE

"" | Out-File -Encoding utf8 -Append $ProofPath
"DEPLOY_EXITCODE=$deployExit" | Out-File -Encoding utf8 -Append $ProofPath
"AFTER_DJANGO_SETTINGS_MODULE=$env:DJANGO_SETTINGS_MODULE" | Out-File -Encoding utf8 -Append $ProofPath

exit $deployExit
