#!/bin/bash
# L.I.V.E - Local Interpretive Vocal Engine
# Native Voice Agent Startup Script

echo "================================================="
echo "  L.I.V.E [ Local Interpretive Vocal Engine ]  "
echo "  MYM LOGIC LLC - Native Voice Agent          "
echo "================================================="
echo ""
echo "Starting L.I.V.E services..."
echo ""
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

echo "✅ Docker detected"
echo "🚀 Launching L.I.V.E environment..."
echo ""
docker-compose up -d

echo ""
echo "================================================="
echo "  ✅ L.I.V.E IS NOW OPERATIONAL               "
echo "================================================="
echo ""
echo "🌐 Frontend: http://localhost:3001"
echo "💬 Rocket.Chat: http://localhost:3000"
echo "🔌 Backend API: http://localhost:5000"
echo "🎙️ L.I.V.E Engine: ACTIVE"
echo ""
echo "=================================================
