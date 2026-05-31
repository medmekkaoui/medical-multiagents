$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Uvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"
$FrontendUrl = "http://127.0.0.1:5500/index.html"
$ApiUrl = "http://127.0.0.1:8000"

function Test-Port {
    param([int]$Port)

    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $connection = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $success = $connection.AsyncWaitHandle.WaitOne(500, $false)
        if ($success) {
            $client.EndConnect($connection)
        }
        $client.Close()
        return $success
    }
    catch {
        return $false
    }
}

if (-not (Test-Path $Python)) {
    Write-Host "Python du venv introuvable: $Python" -ForegroundColor Red
    Write-Host "Lance d'abord: uv sync" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $Uvicorn)) {
    Write-Host "Uvicorn introuvable: $Uvicorn" -ForegroundColor Red
    Write-Host "Installe les dependances puis relance le script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Demarrage du projet Medical Multi-Agents..." -ForegroundColor Cyan

if (Test-Port 8000) {
    Write-Host "Backend deja lance sur $ApiUrl" -ForegroundColor Green
}
else {
    Start-Process `
        -FilePath $Uvicorn `
        -ArgumentList "backend.app.api:app", "--reload", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory $Root `
        -WindowStyle Minimized
    Write-Host "Backend FastAPI lance sur $ApiUrl" -ForegroundColor Green
}

if (Test-Port 5500) {
    Write-Host "Frontend deja lance sur $FrontendUrl" -ForegroundColor Green
}
else {
    Start-Process `
        -FilePath $Python `
        -ArgumentList "-m", "http.server", "5500", "--directory", "frontend" `
        -WorkingDirectory $Root `
        -WindowStyle Minimized
    Write-Host "Frontend React lance sur $FrontendUrl" -ForegroundColor Green
}

Start-Sleep -Seconds 2
Start-Process $FrontendUrl

Write-Host ""
Write-Host "Projet lance." -ForegroundColor Cyan
Write-Host "Frontend : $FrontendUrl"
Write-Host "API      : $ApiUrl/docs"
