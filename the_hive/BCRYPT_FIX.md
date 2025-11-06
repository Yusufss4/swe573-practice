# bcrypt Compatibility Fix

## Issue
The latest bcrypt library (5.x) has breaking changes with passlib that cause errors:
- `AttributeError: module 'bcrypt' has no attribute '__about__'`
- `ValueError: password cannot be longer than 72 bytes`

## Solutions Applied

### 1. Pin bcrypt Version
Updated `pyproject.toml` to use bcrypt 4.x:
```toml
"bcrypt>=4.0.0,<5.0.0"
```

### 2. Handle 72-byte Limit
Updated `app/core/security.py` to properly truncate passwords to 72 bytes:

```python
def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes, hashed_password)
```

## Why 72 bytes?
bcrypt has a hard limit of 72 bytes for passwords. This is more than sufficient for security:
- 72 ASCII characters
- ~18-24 characters for complex UTF-8 passwords
- Industry standard password length limits are typically 32-128 characters

## After Applying Fix

Rebuild the Docker container to install the pinned bcrypt version:

```bash
cd infra
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

Or use the rebuild script:
```bash
./rebuild_docker.sh
```

Then run the sanity check:
```bash
docker-compose exec app python scripts/sanity_check_auth.py
```

## Alternative Solutions

If you still encounter issues, you can:

1. **Use a different algorithm**: Replace bcrypt with argon2
   ```toml
   "passlib[argon2]>=1.7.4"
   ```

2. **Use Python's hashlib**: Implement custom PBKDF2
   ```python
   import hashlib
   import os
   
   def hash_password(password: str) -> str:
       salt = os.urandom(32)
       pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
       return salt.hex() + pwdhash.hex()
   ```

3. **Stick with bcrypt 4.x**: Current recommended approach
