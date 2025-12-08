#!/usr/bin/env python3
"""
Migration script to switch from OpenAI to Gemini API
"""

import os
import sys
from pathlib import Path

def migrate_env_file():
    """Update .env file to use Gemini instead of OpenAI"""
    env_file = Path(".env")

    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env first.")
        return False

    # Read current .env
    with open(env_file, 'r') as f:
        content = f.read()

    # Update API keys and models
    updates = {
        "OPENAI_API_KEY": "GEMINI_API_KEY",
        "OPENAI_MODEL": "GEMINI_MODEL",
        "OPENAI_EMBEDDING_MODEL": "GEMINI_EMBEDDING_MODEL",
        "OPENAI_MAX_TOKENS": "GEMINI_MAX_TOKENS",
        "OPENAI_TEMPERATURE": "GEMINI_TEMPERATURE",
    }

    # Track changes
    changes_made = []

    for old_key, new_key in updates.items():
        if f"{old_key}=" in content:
            # Replace old key with new key
            content = content.replace(f"{old_key}=", f"{new_key}=")
            changes_made.append(f"✅ {old_key} → {new_key}")

    # Update model values if they're OpenAI defaults
    content = content.replace("gpt-4", "gemini-2.0-flash-exp")
    content = content.replace("text-embedding-ada-002", "models/embedding-001")
    changes_made.append("✅ Updated model defaults to Gemini")

    # Update vector size comment
    content = content.replace("# OpenAI", "# Gemini API")

    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)

    if changes_made:
        print("\n📝 Migration completed. Changes made:")
        for change in changes_made:
            print(f"  {change}")
        print("\n⚠️  Please update your GEMINI_API_KEY with your actual Gemini API key.")
        print("   Get your key at: https://makersuite.google.com/app/apikey")
        return True
    else:
        print("\n✅ No migration needed. Already using Gemini configuration.")
        return True

def update_requirements():
    """Update requirements.txt for Gemini"""
    req_file = Path("requirements.txt")

    if not req_file.exists():
        print("❌ requirements.txt not found.")
        return False

    with open(req_file, 'r') as f:
        content = f.read()

    # Replace OpenAI with Google Generative AI
    if "openai==" in content:
        content = content.replace("openai==1.3.7", "google-generativeai==0.3.2")
        content = content.replace("tiktoken==0.5.2", "")

        # Clean up any extra newlines
        content = '\n'.join(line for line in content.split('\n') if line.strip())

        with open(req_file, 'w') as f:
            f.write(content)

        print("✅ Updated requirements.txt")
        print("   Please run: pip install -r requirements.txt")
        return True
    else:
        print("✅ requirements.txt already up to date")
        return True

def main():
    """Run migration"""
    print("🔄 Migrating from OpenAI to Gemini API...\n")

    # Update .env file
    env_ok = migrate_env_file()

    # Update requirements
    req_ok = update_requirements()

    if env_ok and req_ok:
        print("\n✅ Migration successful!")
        print("\nNext steps:")
        print("1. Add your Gemini API key to .env")
        print("2. Run: pip install -r requirements.txt")
        print("3. Restart your application")
        print("\n📚 For more information about Gemini API:")
        print("   https://ai.google.dev/docs")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()