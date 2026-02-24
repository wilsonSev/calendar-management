#!/bin/bash

echo "======================================"
echo "Service Status Check"
echo "======================================"
echo ""

# Check Router (port 50051)
echo "1. Router Service (gRPC):"
if lsof -i :50051 > /dev/null 2>&1; then
    echo "   ✓ Running on port 50051"
else
    echo "   ✗ Not running"
    echo "   → Start with: cd router && go run cmd/router/main.go"
fi
echo ""

# Check Gateway (port 8081)
echo "2. Gateway Service (HTTP):"
if lsof -i :8081 > /dev/null 2>&1; then
    echo "   ✓ Running on port 8081"
else
    echo "   ✗ Not running (optional)"
    echo "   → Start with: cd services/gateway && go run cmd/server/main.go"
fi
echo ""

# Check Python config
echo "3. Python NLP Configuration:"
if [ -f ".env" ]; then
    if grep -q "openrouter=" .env; then
        echo "   ✓ .env file exists with openrouter key"
    else
        echo "   ✗ openrouter key not found in .env"
    fi
else
    echo "   ✗ .env file not found"
fi
echo ""

# Check Python venv
echo "4. Python Virtual Environment:"
if [ -d "nlp/venv" ]; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ✗ Virtual environment not found"
    echo "   → Create with: cd nlp && python3 -m venv venv && pip install -r requirements.txt"
fi
echo ""

echo "======================================"
echo "Quick Start Commands:"
echo "======================================"
echo ""
echo "Start Router:"
echo "  cd router && go run cmd/router/main.go"
echo ""
echo "Test Python NLP:"
echo "  cd nlp && source venv/bin/activate && python check_services.py"
echo ""
