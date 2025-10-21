#!/bin/bash
################################################################################
# Run ggNet Backend Tests
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh storage      # Run storage tests only
#   ./run_tests.sh -v           # Verbose output
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ggNet Backend Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo -e "${BLUE}Installing requirements...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo

if [ "$1" == "storage" ]; then
    pytest tests/test_storage_manager.py -v
elif [ "$1" == "-v" ]; then
    pytest -v
else
    pytest
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Tests completed!${NC}"
echo -e "${GREEN}========================================${NC}"

