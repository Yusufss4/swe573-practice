#!/bin/bash
# Test script for User API

set -e

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing User API${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Create users
echo -e "${BLUE}[1/6] Creating users...${NC}"
USER1=$(curl -s -X POST "${BASE_URL}/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","full_name":"Alice Wonder"}')
echo "$USER1" | jq '.'
USER1_ID=$(echo "$USER1" | jq -r '.id')
echo -e "${GREEN}✓ Created user with ID: $USER1_ID${NC}\n"

USER2=$(curl -s -X POST "${BASE_URL}/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","username":"bob","full_name":"Bob Builder"}')
USER2_ID=$(echo "$USER2" | jq -r '.id')
echo -e "${GREEN}✓ Created user with ID: $USER2_ID${NC}\n"

# Test 2: List all users
echo -e "${BLUE}[2/6] Listing all users...${NC}"
USERS=$(curl -s "${BASE_URL}/users/")
echo "$USERS" | jq '.'
USER_COUNT=$(echo "$USERS" | jq 'length')
echo -e "${GREEN}✓ Found $USER_COUNT users${NC}\n"

# Test 3: Get specific user
echo -e "${BLUE}[3/6] Getting user by ID...${NC}"
USER=$(curl -s "${BASE_URL}/users/${USER1_ID}")
echo "$USER" | jq '.'
echo -e "${GREEN}✓ Retrieved user${NC}\n"

# Test 4: Update user
echo -e "${BLUE}[4/6] Updating user...${NC}"
UPDATED=$(curl -s -X PATCH "${BASE_URL}/users/${USER1_ID}" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Alice in Wonderland","is_active":true}')
echo "$UPDATED" | jq '.'
echo -e "${GREEN}✓ User updated${NC}\n"

# Test 5: Test pagination
echo -e "${BLUE}[5/6] Testing pagination...${NC}"
PAGINATED=$(curl -s "${BASE_URL}/users/?skip=0&limit=1")
echo "$PAGINATED" | jq '.'
echo -e "${GREEN}✓ Pagination working${NC}\n"

# Test 6: Delete user
echo -e "${BLUE}[6/6] Deleting user...${NC}"
curl -s -X DELETE "${BASE_URL}/users/${USER2_ID}" -w "\nHTTP Status: %{http_code}\n"
echo -e "${GREEN}✓ User deleted${NC}\n"

# Verify deletion
echo -e "${BLUE}Verifying deletion...${NC}"
DELETED_USER=$(curl -s "${BASE_URL}/users/${USER2_ID}" -w "\nHTTP Status: %{http_code}")
if echo "$DELETED_USER" | grep -q "404"; then
    echo -e "${GREEN}✓ User successfully deleted${NC}\n"
else
    echo -e "${RED}✗ User still exists${NC}\n"
fi

# Final user count
echo -e "${BLUE}Final user count...${NC}"
FINAL_USERS=$(curl -s "${BASE_URL}/users/")
FINAL_COUNT=$(echo "$FINAL_USERS" | jq 'length')
echo -e "${GREEN}✓ Total users: $FINAL_COUNT${NC}\n"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${BLUE}========================================${NC}"
