#!/bin/bash
# =============================================================================
# DevSkyy Production Smoke Test Script
# =============================================================================
# Tests all critical endpoints after deployment to verify system health.
#
# Usage:
#   ./scripts/smoke-test.sh                    # Use default URLs
#   ./scripts/smoke-test.sh --local            # Test local development
#   ./scripts/smoke-test.sh --staging          # Test staging environment
#   API_URL=https://custom.api.com ./scripts/smoke-test.sh
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
# =============================================================================

set -e

# =============================================================================
# Configuration
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default URLs (production)
API_URL="${API_URL:-https://api.devskyy.app}"
FRONTEND_URL="${FRONTEND_URL:-https://app.devskyy.app}"
WORDPRESS_URL="${WORDPRESS_URL:-https://skyyrose.co}"

# Parse arguments
case "$1" in
    --local)
        API_URL="http://localhost:8000"
        FRONTEND_URL="http://localhost:3000"
        WORDPRESS_URL="http://localhost:8080"
        echo -e "${BLUE}Testing LOCAL environment${NC}"
        ;;
    --staging)
        API_URL="${STAGING_API_URL:-https://staging-api.devskyy.app}"
        FRONTEND_URL="${STAGING_FRONTEND_URL:-https://staging.devskyy.app}"
        # WP.com staging host [live 2026-09-18]; staging.skyyrose.com does not resolve.
        WORDPRESS_URL="${STAGING_WP_URL:-https://staging-7e48-skyyrose.wpcomstaging.com}"
        echo -e "${BLUE}Testing STAGING environment${NC}"
        ;;
    *)
        echo -e "${BLUE}Testing PRODUCTION environment${NC}"
        ;;
esac

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local expected_content="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    # Make request
    local response
    local http_code
    response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 --max-time 30 "$url" 2>/dev/null || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    # Check status code
    if [ "$http_code" -eq "$expected_status" ]; then
        # Check content if specified
        if [ -n "$expected_content" ]; then
            if echo "$body" | grep -q "$expected_content"; then
                echo -e "  ${GREEN}✓${NC} $name (${http_code})"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                return 0
            else
                echo -e "  ${RED}✗${NC} $name - Content mismatch (expected: $expected_content)"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
        else
            echo -e "  ${GREEN}✓${NC} $name (${http_code})"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        fi
    else
        echo -e "  ${RED}✗${NC} $name - HTTP $http_code (expected: $expected_status)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

test_json_field() {
    local name="$1"
    local url="$2"
    local field="$3"
    local expected_value="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    # Make request
    local response
    response=$(curl -s --connect-timeout 10 --max-time 30 "$url" 2>/dev/null || echo "{}")

    # Extract field value (basic JSON parsing)
    local value
    value=$(echo "$response" | grep -o "\"$field\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | cut -d'"' -f4 || echo "")

    if [ "$value" = "$expected_value" ]; then
        echo -e "  ${GREEN}✓${NC} $name ($field=$value)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "  ${RED}✗${NC} $name - $field=\"$value\" (expected: \"$expected_value\")"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# =============================================================================
# Test Suites
# =============================================================================

test_backend_api() {
    print_header "Backend API Tests ($API_URL)"

    # Health endpoints
    test_endpoint "Health check" "$API_URL/health" 200 "healthy"
    test_endpoint "Readiness check" "$API_URL/health/ready" 200
    test_endpoint "Liveness check" "$API_URL/health/live" 200

    # API documentation
    test_endpoint "OpenAPI docs" "$API_URL/docs" 200 "swagger"
    test_endpoint "ReDoc" "$API_URL/redoc" 200

    # Core API endpoints (expect 200 or 401 for auth-required)
    test_endpoint "Agents list" "$API_URL/api/v1/agents" 200

    # Metrics (if enabled)
    test_endpoint "Prometheus metrics" "$API_URL/metrics" 200 "http_requests_total" || true
}

test_frontend() {
    print_header "Frontend Tests ($FRONTEND_URL)"

    # Main pages
    test_endpoint "Dashboard home" "$FRONTEND_URL" 200
    test_endpoint "Agents page" "$FRONTEND_URL/agents" 200
    test_endpoint "3D Pipeline page" "$FRONTEND_URL/3d-pipeline" 200
    test_endpoint "Tools page" "$FRONTEND_URL/tools" 200
    test_endpoint "WordPress page" "$FRONTEND_URL/wordpress" 200

    # API routes
    test_endpoint "Frontend health API" "$FRONTEND_URL/api/health" 200 "ok"
}

test_wordpress() {
    print_header "WordPress Tests ($WORDPRESS_URL)"

    # Main site
    test_endpoint "WordPress home" "$WORDPRESS_URL" 200

    # REST API
    test_endpoint "WP REST API" "$WORDPRESS_URL/wp-json/" 200 "wp/v2"
    test_endpoint "WP Posts" "$WORDPRESS_URL/wp-json/wp/v2/posts" 200

    # WooCommerce (public endpoints)
    test_endpoint "WooCommerce products" "$WORDPRESS_URL/wp-json/wc/v3/products" 200 || \
    test_endpoint "WooCommerce products (auth)" "$WORDPRESS_URL/shop" 200
}

test_security_headers() {
    print_header "Security Headers Tests"

    local url="$FRONTEND_URL"
    local headers
    headers=$(curl -s -I --connect-timeout 10 "$url" 2>/dev/null || echo "")

    TESTS_RUN=$((TESTS_RUN + 1))
    if echo "$headers" | grep -qi "x-content-type-options"; then
        echo -e "  ${GREEN}✓${NC} X-Content-Type-Options header present"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} X-Content-Type-Options header missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    if echo "$headers" | grep -qi "x-frame-options"; then
        echo -e "  ${GREEN}✓${NC} X-Frame-Options header present"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} X-Frame-Options header missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    if echo "$headers" | grep -qi "referrer-policy"; then
        echo -e "  ${GREEN}✓${NC} Referrer-Policy header present"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} Referrer-Policy header missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_cors() {
    print_header "CORS Configuration Tests"

    local response
    response=$(curl -s -I -X OPTIONS \
        -H "Origin: https://app.devskyy.app" \
        -H "Access-Control-Request-Method: POST" \
        --connect-timeout 10 \
        "$API_URL/api/v1/agents" 2>/dev/null || echo "")

    TESTS_RUN=$((TESTS_RUN + 1))
    if echo "$response" | grep -qi "access-control-allow"; then
        echo -e "  ${GREEN}✓${NC} CORS headers present for allowed origin"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} CORS headers check - verify in production"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              DevSkyy Production Smoke Test Suite                          ║${NC}"
echo -e "${BLUE}║              Version 3.0.0                                                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  API:       ${API_URL}"
echo -e "  Frontend:  ${FRONTEND_URL}"
echo -e "  WordPress: ${WORDPRESS_URL}"
echo ""
echo -e "  Started at: $(date)"

# Run test suites
test_backend_api || true
test_frontend || true
test_wordpress || true
test_security_headers || true
test_cors || true

# =============================================================================
# Summary
# =============================================================================

print_header "Test Summary"

echo ""
echo -e "  Tests Run:    ${TESTS_RUN}"
echo -e "  ${GREEN}Passed:${NC}       ${TESTS_PASSED}"
echo -e "  ${RED}Failed:${NC}       ${TESTS_FAILED}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ALL SMOKE TESTS PASSED ✓                              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    SOME TESTS FAILED ✗                                    ║${NC}"
    echo -e "${RED}║                    Review output above for details                        ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"

    echo ""
    echo -e "${YELLOW}Troubleshooting tips:${NC}"
    echo "  1. Check service logs for errors"
    echo "  2. Verify all environment variables are set"
    echo "  3. Ensure database/Redis connections are working"
    echo "  4. Check DNS and SSL certificates"
    echo ""

    exit 1
fi
