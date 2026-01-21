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

$env:DJANGO_SETTINGS_MODULE = "purelaka.settings_prod"

# Write a clear header for auditability
"DEPLOY GATE PROOF" | Out-File -FilePath $ProofPath -Encoding utf8
("Timestamp: " + (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")) | Out-File -FilePath $ProofPath -Append -Encoding utf8
("DJANGO_SETTINGS_MODULE: " + $env:DJANGO_SETTINGS_MODULE) | Out-File -FilePath $ProofPath -Append -Encoding utf8
"" | Out-File -FilePath $ProofPath -Append -Encoding utf8

python manage.py check --deploy *>&1 | Tee-Object -FilePath $ProofPath -Append

Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue
"" | Out-File -FilePath $ProofPath -Append -Encoding utf8
("DJANGO_SETTINGS_MODULE cleared: " + ($env:DJANGO_SETTINGS_MODULE -eq $null)) | Out-File -FilePath $ProofPath -Append -Encoding utf8

Write-Host "Deploy gate proof written to: $ProofPath"
