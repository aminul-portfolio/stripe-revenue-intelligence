# scripts/_capture_cmd.ps1
# Run a command via cmd.exe /c and append its stdout+stderr to a proof file,
# without PowerShell "NativeCommandError"/RemoteException wrapper lines.

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string] $Command,

  [Parameter(Mandatory = $true)]
  [string] $OutFile,

  [hashtable] $Env = @{}
)

$ErrorActionPreference = "Stop"

# Ensure output directory exists
$dir = Split-Path -Parent $OutFile
if ($dir -and -not (Test-Path $dir)) {
  New-Item -ItemType Directory -Path $dir | Out-Null
}

$tmpOut = [System.IO.Path]::GetTempFileName()
$tmpErr = [System.IO.Path]::GetTempFileName()

# Temporarily apply env vars (child cmd.exe inherits)
$oldEnv = @{}
foreach ($k in $Env.Keys) {
  $oldEnv[$k] = $env:$k
  $env:$k = [string]$Env[$k]
}

try {
  $p = Start-Process -FilePath "cmd.exe" `
    -ArgumentList @("/c", $Command) `
    -NoNewWindow -Wait -PassThru `
    -RedirectStandardOutput $tmpOut `
    -RedirectStandardError  $tmpErr

  # Append captured output to proof file (UTF-8)
  if (Test-Path $tmpOut) { Get-Content $tmpOut -Raw | Out-File -Encoding utf8 -Append $OutFile }
  if (Test-Path $tmpErr) { Get-Content $tmpErr -Raw | Out-File -Encoding utf8 -Append $OutFile }

  exit $p.ExitCode
}
finally {
  # Restore env
  foreach ($k in $Env.Keys) {
    if ($null -eq $oldEnv[$k]) { Remove-Item "Env:$k" -ErrorAction SilentlyContinue }
    else { $env:$k = $oldEnv[$k] }
  }

  Remove-Item $tmpOut, $tmpErr -ErrorAction SilentlyContinue
}
