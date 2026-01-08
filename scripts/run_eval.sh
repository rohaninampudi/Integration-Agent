#!/bin/bash
# Convenience script for running evaluations

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Parse arguments
USE_MOCK=false
VERBOSE=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --mock)
            USE_MOCK=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -o|--output)
            OUTPUT="--output $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Generate output filename if not provided
if [ -z "$OUTPUT" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    OUTPUT="--output eval_${GIT_SHA}_${TIMESTAMP}.json"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Integration Agent - Evaluation Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$USE_MOCK" = true ]; then
    echo -e "${GREEN}Running with mock agent...${NC}"
    python tests/eval_harness.py --mock $VERBOSE $OUTPUT
else
    echo -e "${GREEN}Running with real agent...${NC}"
    python tests/eval_harness.py --real $VERBOSE $OUTPUT
fi

echo ""
echo -e "${GREEN}✓ Evaluation complete${NC}"
