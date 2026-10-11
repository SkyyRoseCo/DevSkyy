#!/bin/bash
# DevSkyy Deployment Verification Script
# Verifies that the Vercel deployment is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="${1:-https://devskyy-dashboard.vercel.app}"

echo "================================================"
echo "DevSkyy Deployment Verification"
echo "================================================"
echo "Testing URL: $BASE_URL"
echo ""

# Function to check URL
check_url() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}

    echo -n "Checking $name... "

    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} ($http_code)"
        return 0
    else
        echo -e "${RED}✗${NC} ($http_code, expected $expected_code)"
        return 1
    fi
}

# Function to check for specific content
check_content() {
    local url=$1
    local name=$2
    local search_term=$3

    echo -n "Checking $name content... "

    content=$(curl -s "$url")

    if echo "$content" | grep -q "$search_term"; then
        echo -e "${GREEN}✓${NC} (found '$search_term')"
        return 0
    else
        echo -e "${RED}✗${NC} (missing '$search_term')"
        return 1
    fi
}

# Counter for failures
failures=0

# 1. Core Pages
echo "1. Core Pages"
echo "-------------"
check_url "$BASE_URL" "Homepage" || ((failures++))
check_url "$BASE_URL/agents" "Agents Page" || ((failures++))
check_url "$BASE_URL/ai-tools" "AI Tools Page" || ((failures++))
check_url "$BASE_URL/3d-pipeline" "3D Pipeline" || ((failures++))
check_url "$BASE_URL/round-table" "Round Table" || ((failures++))
check_url "$BASE_URL/ab-testing" "A/B Testing" || ((failures++))
echo ""

# 2. API Endpoints
echo "2. API Endpoints"
echo "----------------"
check_url "$BASE_URL/health" "Health Endpoint" || ((failures++))
echo ""

# 3. HuggingFace Spaces Content
echo "3. HuggingFace Spaces Configuration"
echo "------------------------------------"
check_content "$BASE_URL/ai-tools" "3D Converter" "3D Model Converter" || ((failures++))
check_content "$BASE_URL/ai-tools" "Flux Upscaler" "Flux Upscaler" || ((failures++))
check_content "$BASE_URL/ai-tools" "LoRA Monitor" "LoRA Training Monitor" || ((failures++))
check_content "$BASE_URL/ai-tools" "Product Analyzer" "Product Analyzer" || ((failures++))
check_content "$BASE_URL/ai-tools" "Product Photography" "Product Photography" || ((failures++))
echo ""

# 4. Static Assets
echo "4. Static Assets"
echo "----------------"
check_url "$BASE_URL/favicon.ico" "Favicon" || ((failures++))
echo ""

# 5. Response Time Check
echo "5. Performance Check"
echo "--------------------"
echo -n "Measuring response time... "
start_time=$(date +%s%N)
curl -s "$BASE_URL" > /dev/null
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [ $response_time -lt 3000 ]; then
    echo -e "${GREEN}✓${NC} (${response_time}ms)"
else
    echo -e "${YELLOW}⚠${NC} (${response_time}ms - slower than 3s)"
fi
echo ""

# 6. Security Headers
echo "6. Security Headers"
echo "-------------------"
headers=$(curl -s -I "$BASE_URL")

check_header() {
    local header=$1
    echo -n "Checking $header... "
    if echo "$headers" | grep -qi "$header"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} (missing)"
        return 1
    fi
}

check_header "X-Content-Type-Options"
check_header "X-Frame-Options"
check_header "Strict-Transport-Security"
echo ""

# Summary
echo "================================================"
echo "Verification Summary"
echo "================================================"

if [ $failures -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your deployment is ready to use:"
    echo "  → Frontend: $BASE_URL"
    echo "  → AI Tools: $BASE_URL/ai-tools"
    exit 0
else
    echo -e "${RED}✗ $failures check(s) failed${NC}"
    echo ""
    echo "Please review the errors above and:"
    echo "  1. Check Vercel deployment logs"
    echo "  2. Verify environment variables"
    echo "  3. Ensure backend is running"
    echo "  4. Check HuggingFace spaces are accessible"
    exit 1
fi
