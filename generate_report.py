#!/usr/bin/env python3
"""
TPC Session Report Generator
Uses master prompt to generate reports via OpenAI GPT-4.1 nano
"""

import yaml
import os
import argparse
import requests
import shutil
from pathlib import Path
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

def load_config(file_path="config.yml"):
    """Load configuration from config.yml"""
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)

def setup_input_directory():
    """Clear and recreate _INPUT directory"""
    input_dir = Path("_INPUT")
    
    # Remove existing directory if it exists
    if input_dir.exists():
        shutil.rmtree(input_dir)
        print("🧹 Cleared existing _INPUT directory")
    
    # Create fresh directory
    input_dir.mkdir(exist_ok=True)
    print("📁 Created fresh _INPUT directory")

def download_to_input(url, filename):
    """Download content from URL to _INPUT/filename"""
    try:
        input_path = Path("_INPUT") / filename
        
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Write content based on file type
        if filename.endswith('.csv'):
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
        else:
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
        
        print(f"✅ Downloaded {filename} from URL")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False

def copy_local_to_input(source_path, filename):
    """Copy local file to _INPUT directory"""
    try:
        source = Path(source_path)
        if not source.exists():
            print(f"⚠️  Local file not found: {source_path}")
            return False
        
        dest = Path("_INPUT") / filename
        shutil.copy2(source, dest)
        print(f"✅ Copied local {filename} to _INPUT")
        return True
    except Exception as e:
        print(f"❌ Error copying {filename}: {e}")
        return False

def download_all_sources(config, args):
    """Download all configured and provided data sources"""
    print("\n📥 Downloading data sources...")
    
    success_count = 0
    total_sources = 0
    
    # 1. Always download program sessions
    total_sources += 1
    program_url = config['data_sources']['program_url']
    if download_to_input(program_url, 'program_sessions.html'):
        success_count += 1
    
    # 2. Always download lightning talks
    total_sources += 1
    lightning_url = config['data_sources']['lightning_talks_url']
    if download_to_input(lightning_url, 'lightning_talks.csv'):
        success_count += 1
    
    # 3. Handle participants data
    total_sources += 1
    if args.participants:
        if args.participants.startswith('http'):
            # Download from URL
            if download_to_input(args.participants, 'attendees.csv'):
                success_count += 1
        else:
            # Copy from local file
            if copy_local_to_input(args.participants, 'attendees.csv'):
                success_count += 1
    else:
        # Check for local attendees.csv
        if copy_local_to_input('attendees.csv', 'attendees.csv'):
            success_count += 1
    
    # 4. Handle discussion notes
    total_sources += 1
    if args.notes:
        if args.notes.startswith('http'):
            # Convert Google Docs URL to export format if needed
            notes_url = args.notes
            if 'docs.google.com' in notes_url and '/edit' in notes_url:
                # Convert to export format
                doc_id = notes_url.split('/d/')[1].split('/')[0]
                notes_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            
            if download_to_input(notes_url, 'discussion_notes.txt'):
                success_count += 1
        else:
            # Copy from local file
            if copy_local_to_input(args.notes, 'discussion_notes.txt'):
                success_count += 1
    else:
        # Check for local discussion notes files
        found_local_notes = False
        for ext in ['.txt', '.docx', '.pdf']:
            for pattern in ['discussion_notes', 'notes', 'meeting_notes']:
                filename = f"{pattern}{ext}"
                if copy_local_to_input(filename, 'discussion_notes.txt'):
                    success_count += 1
                    found_local_notes = True
                    break
            if found_local_notes:
                break
        
        if not found_local_notes:
            print("⚠️  No discussion notes found (will proceed without)")
    
    print(f"\n📊 Downloaded {success_count}/{total_sources} data sources successfully")
    return success_count

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

def filter_lightning_talks_for_session(breakout_group):
    """Filter lightning talks CSV data for the specific session"""
    input_dir = Path("_INPUT")
    lightning_file = input_dir / "lightning_talks.csv"
    
    if not lightning_file.exists():
        return None, 0
    
    try:
        import csv
        from io import StringIO
        
        with open(lightning_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse CSV
        reader = csv.DictReader(StringIO(content))
        filtered_talks = []
        
        for row in reader:
            session_col = 'Which session is best fit for your proposed lightning talk?  Some sessions have already filled up but please submit and if full you will be put on a standby list.'
            session_label = row.get(session_col, '')
            
            # Check if this talk matches the target session
            if session_matches(breakout_group, session_label):
                title = row.get('Title of your proposed lightning talk', 'No title')
                author = row.get('Your full name', 'No author') 
                institution = row.get('Your institution', 'No institution')
                abstract = row.get('Abstract of your proposed lightning talk (80-100 words)', 'No abstract')
                
                filtered_talks.append({
                    'title': title,
                    'author': author, 
                    'institution': institution,
                    'abstract': abstract
                })
        
        # Format for the model
        if filtered_talks:
            formatted_talks = []
            for i, talk in enumerate(filtered_talks, 1):
                formatted = f"Talk {i}:\n**Title**: {talk['title']}\n**Author**: {talk['author']}\n**Institution**: {talk['institution']}\n**Abstract**: {talk['abstract']}\n"
                formatted_talks.append(formatted)
            return '\n'.join(formatted_talks), len(filtered_talks)
        else:
            return None, 0
            
    except Exception as e:
        print(f"⚠️  Error filtering lightning talks: {e}")
        return None, 0

def session_matches(target_group, session_label):
    """Check if session label matches target group using flexible matching"""
    if not target_group or not session_label:
        return False
    
    target = target_group.upper().strip()
    session = session_label.upper().strip()
    
    # Exact match
    if target == session:
        return True
    
    # Target contained in session (for acronyms like DWARF)
    if target in session:
        return True
    
    # Session contained in target (for full names)
    if session in target:
        return True
    
    # Word-based matching for partial matches
    target_words = set(target.replace(',', '').replace(':', '').split())
    session_words = set(session.replace(',', '').replace(':', '').split())
    
    # If most target words appear in session
    if len(target_words & session_words) >= min(2, len(target_words)):
        return True
    
    return False

def read_input_files(breakout_group):
    """Read CSV files and return their content as text"""
    input_dir = Path("_INPUT")
    files_content = {}
    
    # Read and filter lightning talks CSV for the specific session
    filtered_talks, talk_count = filter_lightning_talks_for_session(breakout_group)
    if filtered_talks:
        files_content['lightning_talks'] = filtered_talks
        files_content['talk_count'] = talk_count
        print(f"✅ Found {talk_count} lightning talks for session")
    
    # Read attendees CSV  
    attendees_file = input_dir / "attendees.csv"
    if attendees_file.exists():
        try:
            with open(attendees_file, 'r', encoding='utf-8') as f:
                files_content['attendees'] = f.read()
        except Exception as e:
            print(f"⚠️  Error reading attendees.csv: {e}")
    
    # Read discussion notes if available
    notes_file = input_dir / "discussion_notes.txt"
    if notes_file.exists():
        try:
            with open(notes_file, 'r', encoding='utf-8') as f:
                files_content['notes'] = f.read()
        except Exception as e:
            print(f"⚠️  Error reading discussion_notes.txt: {e}")
    
    return files_content

def call_openai_api(client, prompt, config):
    """Make API call using configuration settings"""
    try:
        model_config = config['model']
        model_name = model_config['name']
        
        print(f"🤖 Calling {model_config['provider']} API with model: {model_name}")
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system", 
                    "content": config['system']['system_message']
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=model_config.get('max_tokens', 4000),
            temperature=model_config.get('temperature', 0.7)
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        sys.exit(1)

def check_for_errors(content):
    """Check if the response contains error codes and handle them"""
    lines = content.strip().split('\n')
    if not lines:
        return False, None
    
    first_line = lines[0].strip()
    
    # Check for known error codes
    error_codes = [
        "ERROR: lightning talks URL not accessible",
        "ERROR: program information not found",
        "ERROR: notes URL not found",
        "ERROR: participants URL not found", 
        "ERROR: local files not found",
        "ERROR: missing input"
    ]
    
    for error_code in error_codes:
        if error_code in first_line:
            return True, error_code
    
    return False, None

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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate TPC session reports using OpenAI GPT-4.1 nano',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -g "DWARF"
  %(prog)s --group "Data, Workflows, Agents, and Reasoning Frameworks"
  %(prog)s -g "DWARF" -p "https://example.com/attendees.csv"
  %(prog)s -g "AI" --participants "./local_attendees.csv"
  %(prog)s -g "DWARF" -n "https://docs.google.com/document/d/abc123/edit"
  %(prog)s -g "AI" -p "./attendees.csv" -n "./discussion_notes.docx"
'''
    )
    
    parser.add_argument(
        '-g', '--group',
        required=True,
        help='Breakout group name or acronym (e.g., "DWARF" or "Data, Workflows, Agents, and Reasoning Frameworks")'
    )
    
    parser.add_argument(
        '-p', '--participants',
        help='URL or file path for participant/attendee data (CSV format with First, Last, Organization columns)'
    )
    
    parser.add_argument(
        '-n', '--notes',
        help='URL or file path for discussion notes (DOCX, PDF, or Google Docs URL)'
    )
    
    return parser.parse_args()

def main():
    """Main execution function"""
    print("🚀 TPC Session Report Generator")
    print("=" * 50)
    
    # Parse command line arguments
    args = parse_arguments()
    breakout_group = args.group
    participants_source = args.participants
    notes_source = args.notes
    
    print(f"🎯 Target breakout group: {breakout_group}")
    if participants_source:
        print(f"👥 Participants source: {participants_source}")
    else:
        print("👥 Participants source: Will check for local attendees.csv or proceed without")
    
    if notes_source:
        print(f"📋 Discussion notes: {notes_source}")
    else:
        print("📋 Discussion notes: Will check for local DOCX/PDF files or proceed without")
    
    # Load configuration
    print("\n📖 Loading configuration...")
    config = load_config()
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
    
    # Setup input directory and download all sources
    setup_input_directory()
    download_all_sources(config, args)
    
    # Read the actual CSV files and include in prompt
    print("\n📖 Reading input files...")
    files_content = read_input_files(breakout_group)
    
    # Build prompt with actual data
    full_prompt = f"{master_prompt}\n\nTARGET BREAKOUT GROUP: {breakout_group}\n\n"
    
    if 'lightning_talks' in files_content:
        full_prompt += f"LIGHTNING TALKS CSV DATA:\n{files_content['lightning_talks']}\n\n"
        print("✅ Lightning talks data included")
    
    if 'attendees' in files_content:
        full_prompt += f"ATTENDEES CSV DATA:\n{files_content['attendees']}\n\n"
        print("✅ Attendees data included")
    
    if 'notes' in files_content:
        full_prompt += f"DISCUSSION NOTES:\n{files_content['notes']}\n\n"
        print("✅ Discussion notes included")
    
    # Make API call
    print("\n🔄 Generating report...")
    response_content = call_openai_api(client, full_prompt, config)
    
    # Check for errors in the response
    print("\n🔍 Checking response for errors...")
    has_error, error_code = check_for_errors(response_content)
    
    if has_error:
        print(f"❌ Model returned error: {error_code}")
        print("\n📄 Full response:")
        print(response_content)
        
        # Save error response for debugging
        error_filename = f"error_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        save_output(response_content, error_filename)
        print(f"\n⚠️  Error response saved to: {error_filename}")
        
        # Exit with error code
        sys.exit(1)
    else:
        print("✅ No errors detected in response")
        
        # Save output
        print("\n💾 Saving report...")
        save_output(response_content)
        
        print("\n🎉 Report generation completed!")

if __name__ == "__main__":
    main()
