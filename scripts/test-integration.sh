#!/bin/bash
# Integration test script for NearGravity NEAR Semantic Guard

set -e

echo "🧪 Testing NearGravity NEAR Semantic Guard Integration"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:5000"
FRONTEND_URL="http://localhost:3000"

# Test functions
test_api_health() {
    echo -e "${YELLOW}Testing API health...${NC}"
    response=$(curl -s "$API_URL/near/health" || echo "FAILED")
    if [[ $response == *"healthy"* ]]; then
        echo -e "${GREEN}✅ API health check passed${NC}"
        return 0
    else
        echo -e "${RED}❌ API health check failed${NC}"
        return 1
    fi
}

test_semantic_analysis() {
    local scenario="$1"
    local query="$2"
    echo -e "${YELLOW}Testing semantic analysis: $scenario${NC}"
    
    response=$(curl -s -X POST "$API_URL/near/semantic-guard" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"max_results\": 3}" || echo "FAILED")
    
    if [[ $response == *"semantic_analysis"* ]] && [[ $response == *"results"* ]]; then
        echo -e "${GREEN}✅ $scenario test passed${NC}"
        # Extract key metrics
        outliers=$(echo "$response" | grep -o '"outliers":\[[^]]*\]' | grep -o '\[.*\]' | tr ',' '\n' | wc -l)
        echo "   Outliers detected: $((outliers-1))"
        return 0
    else
        echo -e "${RED}❌ $scenario test failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

test_frontend_availability() {
    echo -e "${YELLOW}Testing frontend availability...${NC}"
    response=$(curl -s -I "$FRONTEND_URL" | head -n 1 || echo "FAILED")
    if [[ $response == *"200 OK"* ]]; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
        return 0
    else
        echo -e "${RED}❌ Frontend is not accessible${NC}"
        return 1
    fi
}

# Main test execution
main() {
    local failed_tests=0
    
    echo "Starting integration tests..."
    echo ""
    
    # Test API health
    if ! test_api_health; then
        ((failed_tests++))
    fi
    
    echo ""
    
    # Test semantic analysis scenarios
    scenarios=(
        "High Trust:climate change latest research"
        "Misinformation:covid vaccine safety"
        "Mixed Signals:artificial intelligence jobs"
        "Economic Uncertainty:economy recession 2024"
    )
    
    for scenario_query in "${scenarios[@]}"; do
        IFS=':' read -r scenario query <<< "$scenario_query"
        if ! test_semantic_analysis "$scenario" "$query"; then
            ((failed_tests++))
        fi
        echo ""
    done
    
    # Test frontend
    if ! test_frontend_availability; then
        ((failed_tests++))
    fi
    
    echo ""
    echo "=========================================="
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Integration is working correctly.${NC}"
        echo ""
        echo -e "${GREEN}🌐 Frontend: $FRONTEND_URL/semantic-guard${NC}"
        echo -e "${GREEN}🔧 API Health: $API_URL/near/health${NC}"
        echo -e "${GREEN}📊 System Status: $API_URL/near/status${NC}"
    else
        echo -e "${RED}❌ $failed_tests test(s) failed.${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "1. Make sure both API and frontend servers are running"
        echo "2. Check that dependencies are installed"
        echo "3. Verify network connectivity"
        exit 1
    fi
}

# Performance test
performance_test() {
    echo -e "${YELLOW}Running performance test...${NC}"
    start_time=$(date +%s%N)
    
    curl -s -X POST "$API_URL/near/semantic-guard" \
        -H "Content-Type: application/json" \
        -d '{"query": "performance test", "max_results": 5}' > /dev/null
    
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    echo "Response time: ${duration}ms"
    if [ $duration -lt 5000 ]; then
        echo -e "${GREEN}✅ Performance test passed (< 5s)${NC}"
    else
        echo -e "${YELLOW}⚠️  Performance test warning (> 5s)${NC}"
    fi
}

# Run tests based on arguments
if [ "$1" = "--performance" ]; then
    performance_test
elif [ "$1" = "--help" ]; then
    echo "Usage: $0 [--performance|--help]"
    echo "  (no args)     Run full integration test suite"
    echo "  --performance Run performance tests only"
    echo "  --help        Show this help message"
else
    main
fi