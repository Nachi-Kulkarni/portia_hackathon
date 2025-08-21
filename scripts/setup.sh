#!/bin/bash

# Insurance Claim Negotiator Setup Script
echo "🚀 Setting up Insurance Claim Negotiator"
echo "========================================"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV (Portia's recommended Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV installed successfully"
else
    echo "✅ UV is already installed"
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.11"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python ${python_version} found"

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
if [ -f "config/pyproject.toml" ]; then
    cp config/pyproject.toml ./pyproject.toml
    uv sync --all-extras
    echo "✅ Dependencies installed successfully"
else
    echo "❌ pyproject.toml not found in config directory"
    exit 1
fi

# Set up environment file
echo "⚙️  Setting up environment configuration..."
if [ -f "config/.env.example" ]; then
    if [ ! -f ".env" ]; then
        cp config/.env.example .env
        echo "✅ Environment file created from template"
        echo "⚠️  Please edit .env file with your actual API keys"
    else
        echo "✅ Environment file already exists"
    fi
else
    echo "❌ .env.example not found in config directory"
    exit 1
fi

# Create necessary directories if they don't exist
echo "📁 Creating additional directories..."
mkdir -p logs
mkdir -p exports
mkdir -p backups
echo "✅ Directory structure complete"

# Make scripts executable
echo "🔧 Setting up script permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
echo "✅ Script permissions set"

# Run basic validation
echo "🧪 Running basic validation..."
if [ -f "src/demo/basic_test.py" ]; then
    echo "Testing basic agent functionality..."
    python3 src/demo/basic_test.py
    if [ $? -eq 0 ]; then
        echo "✅ Basic validation passed"
    else
        echo "⚠️  Basic validation had issues - check your API keys in .env"
    fi
else
    echo "⚠️  Basic test file not found, skipping validation"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual API keys:"
echo "   - PORTIA_CONFIG__PORTIA_API_KEY"
echo "   - PORTIA_CONFIG__OPENAI_API_KEY or PORTIA_CONFIG__ANTHROPIC_API_KEY"
echo "   - HUME_API_KEY and HUME_SECRET_KEY (optional for voice features)"
echo ""
echo "2. Test the installation:"
echo "   python3 src/demo/basic_test.py"
echo ""
echo "3. Run the complete pipeline test:"
echo "   python3 src/demo/full_pipeline_test.py"
echo ""
echo "4. Run tests:"
echo "   python3 -m pytest tests/"
echo ""
echo "📚 See docs/README.md for detailed usage instructions"