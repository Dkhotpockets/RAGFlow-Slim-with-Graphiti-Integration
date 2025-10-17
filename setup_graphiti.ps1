# Setup script for Graphiti integration
# Run this in PowerShell before starting the application

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   RAGFlow Slim - Graphiti Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if OpenAI API key is set
if (-not $env:OPENAI_API_KEY) {
    Write-Host "❌ OPENAI_API_KEY is not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "You need an OpenAI API key for Graphiti to extract entities and relationships." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To set it, run:" -ForegroundColor Green
    Write-Host '  $env:OPENAI_API_KEY = "sk-your-key-here"' -ForegroundColor White
    Write-Host ""
    Write-Host "Or create a .env file with:" -ForegroundColor Green
    Write-Host '  OPENAI_API_KEY=sk-your-key-here' -ForegroundColor White
    Write-Host ""
    
    $response = Read-Host "Do you want to set it now? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        $apiKey = Read-Host "Enter your OpenAI API key" -MaskInput
        $env:OPENAI_API_KEY = $apiKey
        Write-Host "✅ OpenAI API key set for this session" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Graphiti features will not work without an API key" -ForegroundColor Yellow
        Write-Host "   Vector search will still work normally" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ OPENAI_API_KEY is set" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Next Steps" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Docker services:" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Wait for services to start (30 seconds)" -ForegroundColor White
Write-Host ""
Write-Host "3. Run tests:" -ForegroundColor White
Write-Host "   python test_graphiti.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Access Neo4j Browser:" -ForegroundColor White
Write-Host "   http://localhost:7474" -ForegroundColor Cyan
Write-Host "   Username: neo4j" -ForegroundColor White
Write-Host "   Password: graphiti_password" -ForegroundColor White
Write-Host ""
Write-Host "5. Start the Flask app:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
