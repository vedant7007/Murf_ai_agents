"""
Quick test to verify LiveKit connection works
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / "ten-days-of-voice-agents-2025" / "backend" / ".env"
load_dotenv(env_path)

print("=" * 60)
print("🔍 LiveKit Connection Test")
print("=" * 60)

# Check environment variables
livekit_url = os.getenv("LIVEKIT_URL")
api_key = os.getenv("LIVEKIT_API_KEY")
api_secret = os.getenv("LIVEKIT_API_SECRET")

print("\n📋 Environment Variables:")
print(f"   LIVEKIT_URL: {livekit_url}")
print(f"   LIVEKIT_API_KEY: {api_key}")
print(f"   LIVEKIT_API_SECRET: {'*' * len(api_secret) if api_secret else 'NOT SET'}")

# Validate
if not all([livekit_url, api_key, api_secret]):
    print("\n❌ ERROR: Missing environment variables!")
    print("   Make sure .env file exists with all required variables.")
    exit(1)

# Check URL format
if livekit_url.startswith("ws://localhost") or livekit_url.startswith("ws://127.0.0.1"):
    print("\n✅ Using LOCAL LiveKit server")
    print("   Make sure LiveKit server is running:")
    print("   docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev")
elif livekit_url.startswith("wss://"):
    print("\n🌐 Using LiveKit Cloud")
    print("   Make sure your API credentials are valid!")
else:
    print(f"\n⚠️  WARNING: Unusual LIVEKIT_URL format: {livekit_url}")

# Try to connect (basic check)
print("\n🔌 Testing connection...")

try:
    import requests

    # For local server, try HTTP API endpoint
    if livekit_url.startswith("ws://localhost"):
        http_url = livekit_url.replace("ws://", "http://").replace(":7880", ":7881")
        response = requests.get(http_url, timeout=2)

        if response.status_code == 200:
            print(f"✅ LiveKit server is responding at {http_url}")
        else:
            print(f"⚠️  LiveKit server responded with status {response.status_code}")
    else:
        print("   Skipping connection test (Cloud URL - needs full agent to test)")

except requests.exceptions.ConnectionRefused:
    print("❌ ERROR: Cannot connect to LiveKit server!")
    print("   Is the LiveKit server running?")
    print("   Start it with: docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev")
except Exception as e:
    print(f"⚠️  Connection test skipped: {e}")

print("\n" + "=" * 60)
print("🚀 Next Steps:")
print("=" * 60)
print("1. Make sure LiveKit server is running (if using local)")
print("2. Start backend agent: cd backend && python src/agent.py dev")
print("3. Start frontend: cd frontend && npm run dev")
print("4. Open http://localhost:3000")
print("=" * 60)
