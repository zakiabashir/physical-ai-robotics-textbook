#!/usr/bin/env python3
"""
Simple test for Gemini API without full app dependencies
"""

import os

# Set your API key
os.environ["GEMINI_API_KEY"] = "AIzaSyAyITMcW_a1WIpXAb07jYyq_YdnKlBU4RA"

try:
    import google.generativeai as genai
    print("SUCCESS: Google Generative AI imported successfully")

    # Test configuration
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    def test():
        try:
            # Test basic model
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content("What is Physical AI in one sentence?")
            print(f"\nSUCCESS: Chat Response:")
            print(response.text)

            # Test embedding
            result = genai.embed_content(
                model='models/embedding-001',
                content="Physical AI combines AI with robots",
                task_type="retrieval_document"
            )
            print(f"\nSUCCESS: Embedding created (dimension: {len(result['embedding'])})")

            return True
        except Exception as e:
            print(f"\nERROR: Error during API calls: {e}")
            return False

    # Run the test
    success = test()

    if success:
        print("\nSUCCESS: Gemini API is working correctly!")
    else:
        print("\nERROR: Test failed")

except ImportError as e:
    print(f"ERROR: Failed to import Google Generative AI: {e}")
    print("\nMake sure to install: pip install google-generativeai==0.3.2")