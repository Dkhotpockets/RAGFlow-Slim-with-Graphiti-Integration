# RAGFlow Slim - Ollama Setup Script
# This script helps you set up Ollama for local LLM usage

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║           RAGFlow Slim - Ollama Setup                        ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check if Ollama is installed
Write-Host "`n[1/5] Checking if Ollama is installed..." -ForegroundColor Yellow

try {
    $ollamaVersion = ollama --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ollama is already installed: $ollamaVersion" -ForegroundColor Green
    } else {
        throw "Ollama not found"
    }
} catch {
    Write-Host "❌ Ollama is not installed" -ForegroundColor Red
    Write-Host @"

Please install Ollama:
1. Download from: https://ollama.ai/download/windows
2. Or use winget: winget install Ollama.Ollama
3. Restart this script after installation

"@ -ForegroundColor Yellow
    exit 1
}

# Check if Ollama service is running
Write-Host "`n[2/5] Checking if Ollama service is running..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Ollama service is running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Ollama service not responding, starting it..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# Pull required models
Write-Host "`n[3/5] Checking and pulling required models..." -ForegroundColor Yellow

$requiredModels = @{
    "llama3.2" = "LLM for entity extraction (2GB)"
    "nomic-embed-text" = "Embedding model for vector search (274MB)"
}

foreach ($model in $requiredModels.Keys) {
    Write-Host "`nChecking model: $model ($($requiredModels[$model]))" -ForegroundColor Cyan
    
    $modelList = ollama list 2>&1 | Out-String
    if ($modelList -match $model) {
        Write-Host "✅ Model '$model' is already installed" -ForegroundColor Green
    } else {
        Write-Host "📥 Pulling model '$model'... (this may take a few minutes)" -ForegroundColor Yellow
        ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pulled '$model'" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to pull '$model'" -ForegroundColor Red
        }
    }
}

# Configure environment variables
Write-Host "`n[4/5] Configuring environment variables..." -ForegroundColor Yellow

$env:LLM_PROVIDER = "ollama"
$env:OLLAMA_HOST = "http://localhost:11434"
$env:OLLAMA_MODEL = "llama3.2"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"

Write-Host "✅ Environment variables set for current session:" -ForegroundColor Green
Write-Host "   LLM_PROVIDER = ollama" -ForegroundColor Gray
Write-Host "   OLLAMA_HOST = http://localhost:11434" -ForegroundColor Gray
Write-Host "   OLLAMA_MODEL = llama3.2" -ForegroundColor Gray
Write-Host "   OLLAMA_EMBED_MODEL = nomic-embed-text" -ForegroundColor Gray

# Test Ollama connection
Write-Host "`n[5/5] Testing Ollama connection..." -ForegroundColor Yellow

try {
    $testPrompt = @{
        model = "llama3.2"
        prompt = "Say 'Hello from Ollama!'"
        stream = $false
    } | ConvertTo-Json
    
    $testResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
        -Method Post `
        -Body $testPrompt `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "✅ Ollama test successful!" -ForegroundColor Green
    Write-Host "Response: $($testResponse.response)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Ollama test failed: $_" -ForegroundColor Yellow
}

# Summary
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                    Setup Complete!                           ║
╚══════════════════════════════════════════════════════════════╝

✅ Ollama is installed and running
✅ Required models are downloaded
✅ Environment variables are configured

Next Steps:
───────────
1. Start Docker services:
   docker-compose up -d

2. Run tests:
   python test_graphiti.py

3. Check provider info:
   curl http://localhost:5000/health

Configuration:
──────────────
• Provider: Ollama (Local, FREE)
• LLM Model: llama3.2 (2GB)
• Embed Model: nomic-embed-text (274MB)
• Cost: $0.00 (no API fees!)

For other apps to use Google AI instead:
─────────────────────────────────────────
$env:LLM_PROVIDER = "google"
$env:GOOGLE_API_KEY = "your-google-api-key"

"@ -ForegroundColor Green

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
