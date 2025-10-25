#!/bin/bash
# Validate specification format and quality
# Reading Level: Grade 6.0

echo "================================"
echo "Spec Validation Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0
WARNINGS=0

# Check if SPECIFICATIONS.md exists
echo "1. Checking if SPECIFICATIONS.md exists..."
if [ -f "SPECIFICATIONS.md" ]; then
    echo -e "${GREEN}✓${NC} SPECIFICATIONS.md found"
else
    echo -e "${RED}✗${NC} SPECIFICATIONS.md not found"
    ERRORS=$((ERRORS + 1))
    exit 1
fi
echo ""

# Check for SHALL/MUST language in requirements
echo "2. Checking for SHALL/MUST language..."
REQUIREMENT_COUNT=$(grep -c "^#### Requirement:" SPECIFICATIONS.md)
SHALL_COUNT=$(grep -c "SHALL" SPECIFICATIONS.md)
MUST_COUNT=$(grep -c "MUST" SPECIFICATIONS.md)

echo "   Found $REQUIREMENT_COUNT requirements"
echo "   Found $SHALL_COUNT SHALL statements"
echo "   Found $MUST_COUNT MUST statements"

if [ $SHALL_COUNT -gt 0 ] || [ $MUST_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Requirements use SHALL/MUST language"
else
    echo -e "${YELLOW}⚠${NC} Warning: No SHALL/MUST language found"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check for Given/When/Then scenarios
echo "3. Checking for Given/When/Then scenarios..."
SCENARIO_COUNT=$(grep -c "^##### Scenario:" SPECIFICATIONS.md)
GIVEN_COUNT=$(grep -c "^\*\*Given\*\*:" SPECIFICATIONS.md)
WHEN_COUNT=$(grep -c "^\*\*When\*\*:" SPECIFICATIONS.md)
THEN_COUNT=$(grep -c "^\*\*Then\*\*:" SPECIFICATIONS.md)

echo "   Found $SCENARIO_COUNT scenarios"
echo "   Found $GIVEN_COUNT Given statements"
echo "   Found $WHEN_COUNT When statements"
echo "   Found $THEN_COUNT Then statements"

if [ $SCENARIO_COUNT -gt 0 ] && [ $GIVEN_COUNT -gt 0 ] && [ $WHEN_COUNT -gt 0 ] && [ $THEN_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Scenarios use Given/When/Then format"
else
    echo -e "${YELLOW}⚠${NC} Warning: Incomplete Given/When/Then format"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check for domain sections
echo "4. Checking for domain sections..."
DOMAIN_SECTIONS=(
    "## Core Specifications"
    "## Editor Specifications"
    "## Preview Specifications"
    "## Git Specifications"
    "## Conversion Specifications"
    "## User Interface Specifications"
)

MISSING_DOMAINS=()
for domain in "${DOMAIN_SECTIONS[@]}"; do
    if grep -q "$domain" SPECIFICATIONS.md; then
        echo -e "${GREEN}✓${NC} Found: $domain"
    else
        echo -e "${RED}✗${NC} Missing: $domain"
        MISSING_DOMAINS+=("$domain")
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check reading level
echo "5. Checking reading level..."
if [ -f "check_readability.py" ]; then
    READING_LEVEL=$(python3 check_readability.py SPECIFICATIONS.md 2>/dev/null | grep "^SPECIFICATIONS.md" | awk '{print $2}')
    if [ ! -z "$READING_LEVEL" ]; then
        echo "   Reading level: Grade $READING_LEVEL"
        # Check if reading level is acceptable (< 10.0)
        if (( $(echo "$READING_LEVEL < 10.0" | bc -l) )); then
            echo -e "${GREEN}✓${NC} Reading level is acceptable (< Grade 10)"
        else
            echo -e "${YELLOW}⚠${NC} Warning: Reading level is high (target: Grade 6.0)"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "${YELLOW}⚠${NC} Could not determine reading level"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} check_readability.py not found, skipping reading level check"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check for version info
echo "6. Checking for version and metadata..."
if grep -q "^\*\*Version\*\*:" SPECIFICATIONS.md; then
    echo -e "${GREEN}✓${NC} Version info found"
else
    echo -e "${RED}✗${NC} Version info missing"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "^\*\*Reading Level\*\*:" SPECIFICATIONS.md; then
    echo -e "${GREEN}✓${NC} Reading level metadata found"
else
    echo -e "${RED}✗${NC} Reading level metadata missing"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "^\*\*Last Updated\*\*:" SPECIFICATIONS.md; then
    echo -e "${GREEN}✓${NC} Last updated date found"
else
    echo -e "${YELLOW}⚠${NC} Warning: Last updated date missing"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "================================"
echo "Validation Summary"
echo "================================"
echo ""
echo "Requirements:     $REQUIREMENT_COUNT"
echo "Scenarios:        $SCENARIO_COUNT"
echo "Errors:           $ERRORS"
echo "Warnings:         $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Validation PASSED${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ But there are $WARNINGS warnings to review${NC}"
    fi
    exit 0
else
    echo -e "${RED}✗ Validation FAILED with $ERRORS errors${NC}"
    exit 1
fi
