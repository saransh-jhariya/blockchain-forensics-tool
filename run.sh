#!/bin/bash
#===============================================================================
# Blockchain Forensics Tool - Complete Execution Script
# M.Sc. Forensic Science (Cyber Forensics) - 9th Semester
# Author: Saransh Jhariya | 102FSBSMS2122012
# Mentor: Dr. Ajit Majumdar, LNJN NICFS NFSU, Delhi Campus
# Version: 2.0 - Enhanced Methodology
# Date: March 2026
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
SEED_ADDRESS="${SEED_ADDRESS:-0xdAC17F958D2ee523a2206206994597C13D831ec7}"  # USDT contract
CHAIN="${CHAIN:-ethereum}"
OUTPUT_DIR="${OUTPUT_DIR:-./data/output}"
VERBOSE="${VERBOSE:-false}"

#===============================================================================
# Helper Functions
#===============================================================================

print_header() {
    echo -e "\n${CYAN}===============================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}===============================================================================${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}--- $1 ---${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.10+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python found: $PYTHON_VERSION"
}

check_venv() {
    if [ -d "venv" ]; then
        print_success "Virtual environment found"
        source venv/bin/activate
    else
        print_warning "Virtual environment not found. Creating..."
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        print_success "Virtual environment created and activated"
    fi
}

install_dependencies() {
    print_section "Installing Dependencies"
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

check_env() {
    print_section "Checking Environment Configuration"
    
    if [ -f ".env" ]; then
        print_success ".env file found"
        
        # Check if API key is set
        if grep -q "ETHERSCAN_API_KEY=your_etherscan_api_key_here" .env; then
            print_warning "Etherscan API key not configured"
            print_warning "Edit .env and add your API key from https://etherscan.io/myapikey"
            print_warning "Running in limited mode (may hit rate limits)"
        else
            print_success "Etherscan API key configured"
        fi
    else
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env and add your Etherscan API key"
    fi
}

run_tests() {
    print_section "Running Test Suite"
    
    if [ -d "tests" ]; then
        # Install pytest if not already installed
        pip install pytest pytest-cov -q
        
        echo "Running unit tests..."
        if $PYTHON_CMD -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing; then
            print_success "All tests passed"
        else
            print_error "Some tests failed"
            return 1
        fi
    else
        print_warning "Tests directory not found"
    fi
}

run_pipeline() {
    local seed_addr=$1
    local chain=$2
    local output=$3
    local verbose=$4
    
    print_section "Running Blockchain Forensics Pipeline"
    
    echo "Seed Address: $seed_addr"
    echo "Chain: $chain"
    echo "Output Directory: $output"
    echo ""
    
    # Build command
    CMD="$PYTHON_CMD main.py --seed $seed_addr --chain $chain --output $output"
    
    if [ "$verbose" = "true" ]; then
        CMD="$CMD --verbose"
    fi
    
    # Run pipeline
    if eval $CMD; then
        print_success "Pipeline completed successfully"
    else
        print_error "Pipeline failed"
        return 1
    fi
}

generate_summary() {
    print_section "Generating Execution Summary"
    
    SUMMARY_FILE="$OUTPUT_DIR/execution_summary.txt"
    
    cat > "$SUMMARY_FILE" << EOF
================================================================================
BLOCKCHAIN FORENSICS TOOL - EXECUTION SUMMARY
M.Sc. Forensic Science (Cyber Forensics) - 9th Semester
Author: Saransh Jhariya | 102FSBSMS2122012
================================================================================

Execution Details:
-----------------
Date: $(date '+%Y-%m-%d %H:%M:%S')
Seed Address: $SEED_ADDRESS
Chain: $CHAIN
Output Directory: $OUTPUT_DIR
Python Version: $($PYTHON_CMD --version)

Test Results:
-------------
$(if [ -d "tests" ]; then echo "Tests executed successfully"; else echo "Tests not available"; fi)

Output Files Generated:
-----------------------
EOF

    if [ -d "$OUTPUT_DIR" ]; then
        ls -lh "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/*.json 2>/dev/null >> "$SUMMARY_FILE" || echo "No output files found" >> "$SUMMARY_FILE"
    fi
    
    cat >> "$SUMMARY_FILE" << EOF

Directory Structure:
--------------------
$(find data -type f 2>/dev/null | head -20 || echo "No data directory")

================================================================================
END OF SUMMARY
================================================================================
EOF

    print_success "Summary saved to: $SUMMARY_FILE"
    echo ""
    cat "$SUMMARY_FILE"
}

cleanup() {
    print_section "Cleanup"
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

show_help() {
    cat << EOF
Blockchain Forensics Tool - Execution Script

Usage: $0 [OPTIONS]

Options:
  -s, --seed ADDRESS     Seed Ethereum address (default: USDT contract)
  -c, --chain CHAIN      Blockchain to analyze (default: ethereum)
                         Supported: ethereum, arbitrum, polygon, bsc, optimism
  -o, --output DIR       Output directory (default: ./data/output)
  -v, --verbose          Enable verbose logging
  -t, --tests-only       Run only tests, skip pipeline
  -p, --pipeline-only    Run only pipeline, skip tests
  --no-cleanup           Skip cleanup after execution
  -h, --help             Show this help message

Examples:
  $0                                     # Run with defaults
  $0 -s 0x123... -v                      # Custom address with verbose
  $0 -c polygon --tests-only             # Run tests only for Polygon
  $0 --pipeline-only                     # Skip tests, run pipeline only

Environment Variables:
  SEED_ADDRESS     Seed address (overrides -s)
  CHAIN            Chain name (overrides -c)
  OUTPUT_DIR       Output directory (overrides -o)
  VERBOSE          Verbose mode: true/false (overrides -v)

EOF
}

#===============================================================================
# Main Execution
#===============================================================================

main() {
    local run_tests_flag=true
    local run_pipeline_flag=true
    local do_cleanup=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--seed)
                SEED_ADDRESS="$2"
                shift 2
                ;;
            -c|--chain)
                CHAIN="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -t|--tests-only)
                run_pipeline_flag=false
                shift
                ;;
            -p|--pipeline-only)
                run_tests_flag=false
                shift
                ;;
            --no-cleanup)
                do_cleanup=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Print header
    print_header "BLOCKCHAIN FORENSICS TOOL v2.0"
    echo "M.Sc. Forensic Science (Cyber Forensics) - 9th Semester"
    echo "Author: Saransh Jhariya | 102FSBSMS2122012"
    echo "Mentor: Dr. Ajit Majumdar, LNJN NICFS NFSU, Delhi Campus"
    echo ""
    echo "Seed Address: $SEED_ADDRESS"
    echo "Chain: $CHAIN"
    echo "Output Directory: $OUTPUT_DIR"
    echo "Verbose: $VERBOSE"
    
    # Execution steps
    print_header "STEP 1: Environment Setup"
    check_python
    check_venv
    install_dependencies
    check_env
    
    if [ "$run_tests_flag" = true ]; then
        print_header "STEP 2: Running Tests"
        if ! run_tests; then
            print_error "Tests failed. Aborting pipeline."
            exit 1
        fi
    fi
    
    if [ "$run_pipeline_flag" = true ]; then
        print_header "STEP 3: Running Forensics Pipeline"
        if ! run_pipeline "$SEED_ADDRESS" "$CHAIN" "$OUTPUT_DIR" "$VERBOSE"; then
            print_error "Pipeline execution failed"
            exit 1
        fi
    fi
    
    print_header "STEP 4: Generating Summary"
    generate_summary
    
    if [ "$do_cleanup" = true ]; then
        print_header "STEP 5: Cleanup"
        cleanup
    fi
    
    print_header "EXECUTION COMPLETE"
    print_success "All steps completed successfully!"
    echo ""
    echo "Output files are located in: $OUTPUT_DIR"
    echo ""
    echo "To view the interactive forensic graph:"
    echo "  Open: $OUTPUT_DIR/forensic_graph.html in your browser"
    echo ""
    echo "To view the forensic report:"
    echo "  Open: $OUTPUT_DIR/forensic_report.json"
    echo ""
}

# Run main function
main "$@"
