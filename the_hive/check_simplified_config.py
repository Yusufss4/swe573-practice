from app.core.config import settings

print("Configuration after simplification:")
print(f"  APP_NAME: {settings.APP_NAME}")
print(f"  DATABASE_URL: {settings.DATABASE_URL}")
print(f"  HOST: {settings.HOST}")
print(f"  PORT: {settings.PORT}")
print(f"  RELOAD: {settings.RELOAD}")
print(f"\nRemoved:")
print("  ✓ APP_ENV (development/staging/production)")
print("  ✓ DEBUG flag")
print("  ✓ is_development() property")
print("  ✓ is_production() property")
print(f"\nSettings attributes: {[a for a in dir(settings) if not a.startswith('_')]}")
