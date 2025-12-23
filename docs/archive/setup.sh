#!/bin/bash
# OpenRouter Integration - Quick Setup Script

set -e

echo "============================================"
echo "OpenRouter API Integration - Setup"
echo "============================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo -e "${RED}Error: Python 3.9+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env if it doesn't exist
echo -e "\n${YELLOW}Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your OPENROUTER_API_KEY${NC}"
else
    echo -e "${GREEN}✓ .env exists${NC}"
fi

# Check if API key is set
if grep -q "OPENROUTER_API_KEY=sk-or-v1-" .env; then
    echo -e "${GREEN}✓ API key appears to be configured${NC}"
else
    echo -e "${RED}⚠ API key not configured in .env${NC}"
    echo -e "${YELLOW}Please add your API key to .env:${NC}"
    echo -e "  OPENROUTER_API_KEY=sk-or-v1-your-key-here"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Run basic validation
echo -e "\n${YELLOW}Running validation...${NC}"
python3 -c "from config.settings import get_settings; get_settings()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration valid${NC}"
else
    echo -e "${RED}⚠ Configuration validation failed${NC}"
fi

# Display next steps
echo -e "\n============================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API key in .env:"
echo "   nano .env"
echo ""
echo "2. Test the installation:"
echo "   python examples/basic_usage.py"
echo ""
echo "3. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "4. View documentation:"
echo "   cat README.md"
echo ""
echo "============================================"
echo ""

# Optional: Test API connection
read -p "Test API connection now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Testing API connection...${NC}"
    python3 -c "
from src.openrouter import OpenRouterClient, Message
try:
    client = OpenRouterClient()
    messages = [Message(role='user', content='Say hello')]
    response = client.chat_completion(messages)
    print('✓ API connection successful!')
    print(f'Response: {response.choices[0].message.content}')
except Exception as e:
    print(f'✗ API connection failed: {e}')
"
fi

echo ""
echo -e "${GREEN}Setup script complete!${NC}"
