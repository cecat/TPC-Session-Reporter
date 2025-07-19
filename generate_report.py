#!/usr/bin/env python3
"""
TPC Session Report Generator
Uses master prompt to generate reports via OpenAI GPT-4.1 nano
"""

import yaml
import os
from openai import OpenAI
from datetime import datetime
import sys

def load_secrets(file_path="secrets.yml"):
    """Load API credentials from secrets.yml"""
    try:
        with open(file_path, 'r') as f:
            secrets = yaml.safe_load(f)
        return secrets.get('openai_api_key')
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        sys.exit(1)

def load_master_prompt(file_path="tpc25_master_prompt.yaml"):
    """Load the master prompt from YAML file"""
    try:
        with open(file_path, 'r') as f:
            prompt_data = yaml.safe_load(f)
        return prompt_data.get('master_prompt')
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading master prompt: {e}")
        sys.exit(1)

def call_openai_api(client, prompt, model="gpt-4o-mini-2024-07-18"):
    """Make API call to OpenAI GPT-4.1 nano"""
    try:
        print(f"🤖 Calling OpenAI API with model: {model}")
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that generates detailed session reports for technical conferences."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=4000,  # Adjust based on your needs
            temperature=0.7   # Adjust for creativity vs consistency
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        sys.exit(1)

def save_output(content, filename="draft_report.txt"):
    """Save the generated content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Add header with timestamp
            f.write(f"# TPC Session Report Draft\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Model: GPT-4.1 nano\n\n")
            f.write(content)
        
        print(f"✅ Report saved to: {filename}")
        print(f"📄 File size: {len(content)} characters")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    print("🚀 TPC Session Report Generator")
    print("=" * 50)
    
    # Load configuration
    print("📖 Loading configuration...")
    api_key = load_secrets()
    master_prompt = load_master_prompt()
    
    if not api_key:
        print("❌ Error: OpenAI API key not found in secrets.yml")
        sys.exit(1)
    
    if not master_prompt:
        print("❌ Error: Master prompt not found in tpc25_master_prompt.yaml")
        sys.exit(1)
    
    print("✅ Configuration loaded successfully")
    
    # Set up OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Make API call
    print("\n🔄 Generating report...")
    response_content = call_openai_api(client, master_prompt)
    
    # Save output
    print("\n💾 Saving report...")
    save_output(response_content)
    
    print("\n🎉 Report generation completed!")

if __name__ == "__main__":
    main()
