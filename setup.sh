#!/bin/bash
# TPC Session Reporter Setup Script for macOS

echo "🚀 Setting up TPC Session Reporter environment..."
echo "================================================="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Error: Conda is not installed or not in PATH"
    echo "💡 Please install Miniconda or Anaconda first:"
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"

# Create conda environment
echo "📦 Creating conda environment 'tpc-reporter'..."
conda env create -f environment.yml

# Check if environment was created successfully
if [ $? -eq 0 ]; then
    echo "✅ Environment created successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Activate the environment:"
    echo "   conda activate tpc-reporter"
    echo ""
    echo "2. Run the report generator:"
    echo "   python generate_report.py"
    echo ""
    echo "3. When done, deactivate with:"
    echo "   conda deactivate"
else
    echo "❌ Error: Failed to create conda environment"
    exit 1
fi
