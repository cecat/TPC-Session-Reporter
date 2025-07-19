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

## Output

The script generates a `draft_report.txt` file with the GPT-4.1 nano response.

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
