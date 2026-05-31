$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Stop-Port {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        Where-Object { $_.State -eq "Listen" }

    foreach ($connection in $connections) {
        $processId = $connection.OwningProcess
        if ($processId) {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "Arret du processus sur le port $Port : $($process.ProcessName) ($processId)" -ForegroundColor Yellow
                Stop-Process -Id $processId -Force
            }
        }
    }
}

Write-Host "Redemarrage complet du projet..." -ForegroundColor Cyan
Stop-Port 8000
Stop-Port 5500

Start-Sleep -Seconds 1
& (Join-Path $Root "start_project.ps1")
