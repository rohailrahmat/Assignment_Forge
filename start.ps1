# AssignmentForge - Start Both Servers
Write-Host ""
Write-Host "  ⚡ AssignmentForge - Starting..." -ForegroundColor Cyan
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# Start Backend
Write-Host "  [1/2] Starting Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; C:\Users\rohai\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py" -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Frontend
Write-Host "  [2/2] Starting Frontend (Vite)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "  ✅ AssignmentForge is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  🌐 App:     http://localhost:5173" -ForegroundColor Cyan
Write-Host "  🔧 API:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "  📋 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"
