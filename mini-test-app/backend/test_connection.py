"""Quick test script to verify Gemini API connection."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    print("Please create a .env file with your API key:")
    print("GEMINI_API_KEY=your_api_key_here")
    exit(1)

print("✓ Found GEMINI_API_KEY in .env")
print(f"✓ API Key: {api_key[:10]}...{api_key[-5:]}")

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test connection
    print("\n🧪 Testing Gemini API connection...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content("Say 'Hello, Gemini is working!'")
    
    print("✓ Gemini API connected successfully!")
    print(f"✓ Test response: {response.text}")
    
    print("\n🎉 Setup is complete! You can now run the app:")
    print("   python app.py")
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to connect to Gemini API")
    print(f"Error: {str(e)}")
    print("\nPlease check:")
    print("1. Your API key is correct")
    print("2. You have internet connection")
    print("3. The API key has proper permissions")
