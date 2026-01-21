param(
  [string]$ProofPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProofPath)) {
  $date = Get-Date -Format "yyyy-MM-dd"
  $ProofPath = "docs/proof/m3_deploy_gate_${date}.txt"
}

New-Item -ItemType Directory -Force -Path (Split-Path $ProofPath) | Out-Null

# Important: deploy check only. Do not run tests under settings_prod.
$env:DJANGO_SETTINGS_MODULE = "purelaka.settings_prod"

python manage.py check --deploy *>&1 | Tee-Object -FilePath $ProofPath

Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue

Write-Host "Deploy gate proof written to: $ProofPath"
