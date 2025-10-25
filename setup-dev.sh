#!/bin/bash

# SSH Creator Helper - Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up SSH Creator Helper development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements-test.txt

# Install pre-commit hooks
echo -e "${BLUE}Installing pre-commit hooks...${NC}"
pre-commit install

# Make script executable
echo -e "${BLUE}Making SSH script executable...${NC}"
chmod +x ssh_auth_manager.sh

# Run initial tests
echo -e "${BLUE}Running initial tests...${NC}"
python -m pytest tests/ -v --tb=short

echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo
echo -e "${YELLOW}To activate the environment, run:${NC}"
echo -e "${BLUE}source venv/bin/activate${NC}"
echo
echo -e "${YELLOW}To run tests:${NC}"
echo -e "${BLUE}make test${NC}"
echo
echo -e "${YELLOW}To run linting:${NC}"
echo -e "${BLUE}make lint${NC}"
echo
echo -e "${YELLOW}To run all CI checks:${NC}"
echo -e "${BLUE}make ci-test${NC}"
