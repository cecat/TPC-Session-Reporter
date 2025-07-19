# TPC Session Reporter

AI Agent to create draft conference breakout session reports using OpenAI GPT-4.1 nano and structured prompts.

## Quick Setup (macOS with Conda)

### Option 1: Automated Setup
```bash
./setup.sh
conda activate tpc-reporter
python generate_report.py
```

### Option 2: Manual Setup
```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate tpc-reporter

# Run the report generator
python generate_report.py
```

## Alternative Setup (pip)

If you prefer using pip instead of conda:
```bash
pip install -r requirements.txt
python generate_report.py
```

## Configuration

Ensure you have:
1. **secrets.yml** - Contains your OpenAI API key
2. **tpc25_master_prompt.yaml** - Contains the master prompt template
3. **config.yml** - Contains model settings and data source URLs

### Model Configuration (config.yml)

The `config.yml` file allows you to easily switch between different AI providers and models:

```yaml
model:
  provider: "openai"  # or "azure", "anthropic"
  name: "gpt-4o-mini-2024-07-18"
  endpoint: "https://api.openai.com/v1"
  max_tokens: 4000
  temperature: 0.7

data_sources:
  lightning_talks_url: "https://docs.google.com/spreadsheets/d/..."
  program_url: "https://tpc25.org/sessions/"
```

To use a different model, simply update the configuration file without modifying the code.

## Usage

The TPC Session Reporter can be run using various command line options to customize the data sources.

### Command Line Arguments
- `-g` or `--group`: Specify the breakout group name or acronym. **Required.**
- `-p` or `--participants`: (Optional) Specify the URL or file path for participant/attendee data in CSV format. Defaults to checking for local `attendees.csv` if not provided.
- `-n` or `--notes`: (Optional) Specify the URL or file path for discussion notes (DOCX, PDF, or Google Docs URL). Defaults to checking for local files.
- `-h` or `--help`: Show help message with usage examples

```bash
# View all available options
python generate_report.py --help
```

### Examples
- **Basic usage** (checks for local `attendees.csv`):
  ```bash
  python generate_report.py -g "DWARF"
  ```
- **With participant URL**:
  ```bash
  python generate_report.py -g "DWARF" -p "https://example.com/attendees.csv"
  ```
- **With local participant file**:
  ```bash
  python generate_report.py -g "AI" -p "./local_attendees.csv"
  ```
- **With discussion notes URL**:
  ```bash
  python generate_report.py -g "DWARF" -n "https://docs.google.com/document/d/abc123/export?format=txt"
  ```
- **With local notes file**:
  ```bash
  python generate_report.py -g "AI" -n "./meeting_notes.docx"
  ```
- **Full session name**:
  ```bash
  python generate_report.py -g "Data Workflows, Agents, and Reasoning Frameworks"
  ```
- **Complete example with all options**:
  ```bash
  python generate_report.py -g "DWARF" -p "./attendees.csv" -n "./discussion_notes.docx"
  ```

### Intelligent Session Matching
The tool uses intelligent matching to find sessions based on your group input:
- **Exact matches**: Full session names
- **Acronym matching**: "DWARF" matches "Data Workflows, Agents, and Reasoning Frameworks (DWARF)"
- **Partial matching**: "AI Decision" matches "AI in Decision Sciences"
- **Keyword matching**: "Performance" matches "Performance Evaluation and Measurement"

### Data Sources
- **Lightning Talk Data**: Automatically fetched from Google Sheets URL
- **Session Metadata**: Scraped from https://tpc25.org/sessions/
- **Participant Data**: 
  - If `-p` specified: Uses the provided URL or file path
  - If `-p` not specified: Looks for local `attendees.csv`
  - If no participant data found: Shows "Attendees list not available" in report
- **Discussion Notes**:
  - If `-n` specified: Uses the provided URL or file path
  - If `-n` not specified: Looks for local DOCX or PDF files
  - If no discussion notes found: Proceeds without notes (graceful degradation)

### Expected File Formats
- **Participant/Attendee CSV**: Should have columns `First`, `Last`, `Organization`
- **Discussion Notes**: DOCX or PDF format with session discussion notes, or Google Docs URLs
- **Lightning Talk Data**: Automatically handled from Google Sheets (columns C, D, F, G, H)

**Google Docs URLs**: To use Google Docs as notes source, convert the sharing URL:
- From: `https://docs.google.com/document/d/ABC123/edit?usp=sharing`
- To: `https://docs.google.com/document/d/ABC123/export?format=txt`

### Error Handling
The tool includes intelligent error detection:
- **ERROR: missing input**: Required files are missing
- **ERROR: session not found**: No matching session found (shows available sessions)
- **ERROR: data validation failed**: Data format issues

Error responses are saved to timestamped files for debugging.

## Output

The script generates a `draft_report.txt` file with the GPT-4.1 nano response containing:
- Session report (2-4 pages)
- Appendix A: Attendee list (or "Attendees list not available")
- Appendix B: Lightning talk abstracts

## Environment Management

```bash
# Activate environment
conda activate tpc-reporter

# Deactivate when done
conda deactivate

# Update environment if needed
conda env update -f environment.yml

# Remove environment
conda env remove -n tpc-reporter
```
