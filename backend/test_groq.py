from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

try:
    client = Groq(api_key=api_key)
    
    # Test API call
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello, I am working!' if you can read this.",
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=50,
    )
    
    print("✅ SUCCESS! Groq API is working!")
    print(f"Response: {chat_completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
