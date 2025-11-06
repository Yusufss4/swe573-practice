#!/bin/bash
# Quick test script for authentication system
# Run this inside Docker container

set -e

echo "======================================"
echo "AUTH SYSTEM QUICK TESTS"
echo "======================================"
echo

# Test 1: Check if auth endpoints are registered
echo "1. Checking if auth router is registered..."
python3 -c "
from app.main import app
routes = [r.path for r in app.routes]
auth_routes = [r for r in routes if '/auth/' in r]
print(f'  Found {len(auth_routes)} auth routes:')
for route in auth_routes:
    print(f'    - {route}')
assert len(auth_routes) >= 4, 'Should have at least 4 auth routes'
print('  ✅ Auth router registered')
"

# Test 2: Password hashing
echo
echo "2. Testing password hashing..."
python3 -c "
from app.core.security import get_password_hash, verify_password

password = 'TestPassword123!'
hashed = get_password_hash(password)

assert hashed != password, 'Should be hashed'
assert hashed.startswith('\$2b\$'), 'Should use bcrypt'
assert verify_password(password, hashed), 'Verification should work'
assert not verify_password('wrong', hashed), 'Wrong password should fail'

print(f'  ✅ Password hashing works')
print(f'  ✅ Hash: {hashed[:29]}...')
"

# Test 3: JWT token generation
echo
echo "3. Testing JWT token generation..."
python3 -c "
from app.core.security import create_access_token, decode_access_token

data = {'sub': 1, 'username': 'testuser', 'role': 'user'}
token = create_access_token(data)

assert len(token) > 0, 'Token should not be empty'
assert token.count('.') == 2, 'JWT should have 3 parts'

decoded = decode_access_token(token)
assert decoded is not None, 'Should decode'
assert decoded['sub'] == 1, 'User ID should match'

print(f'  ✅ JWT generation works')
print(f'  ✅ Token: {token[:50]}...')
"

# Test 4: Run pytest
echo
echo "4. Running pytest auth tests..."
pytest tests/test_auth.py -v --tb=short

echo
echo "======================================"
echo "✅ ALL QUICK TESTS PASSED"
echo "======================================"
echo
echo "Next: Test via HTTP"
echo "  1. Start server: uvicorn app.main:app --reload"
echo "  2. Register: curl -X POST http://localhost:8000/api/v1/auth/register ..."
echo "  3. Login: curl -X POST http://localhost:8000/api/v1/auth/login ..."
echo "  4. Get me: curl -X GET http://localhost:8000/api/v1/auth/me -H 'Authorization: Bearer TOKEN'"
