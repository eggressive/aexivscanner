#!/bin/bash
# Helper script for easily setting fair value source priority

show_help() {
    echo "AEX DCF Scanner - Fair Value Priority Configuration"
    echo ""
    echo "Usage: ./set_fair_value_priority.sh [option]"
    echo ""
    echo "Options:"
    echo "  --dcf-first    Set DCF model as primary source (default)"
    echo "  --manual-first Set manual values as primary source"
    echo "  --analyst-first Set analyst targets as primary source"
    echo "  --custom       Specify custom priority order"
    echo "  --current      View current priority configuration"
    echo "  --help         Show this help message"
    echo ""
    echo "Example:"
    echo "  ./set_fair_value_priority.sh --dcf-first"
    echo "  ./set_fair_value_priority.sh --custom dcf analyst manual"
    echo ""
}

# Check if config_manager.py exists
if [ ! -f "config_manager.py" ]; then
    echo "Error: config_manager.py not found. Please run this script from the project root directory."
    exit 1
fi

# Current configuration
if [ "$1" == "--current" ]; then
    grep -A 5 "\"priority\"" fair_values_config.json
    exit 0
fi

# Help
if [ "$1" == "--help" ] || [ -z "$1" ]; then
    show_help
    exit 0
fi

# DCF first (default configuration)
if [ "$1" == "--dcf-first" ]; then
    echo "Setting DCF as primary fair value source..."
    python config_manager.py --set-priority dcf manual analyst
    echo "Done! DCF values will now be used as the primary fair value source."
    exit 0
fi

# Manual values first
if [ "$1" == "--manual-first" ]; then
    echo "Setting manual values as primary fair value source..."
    python config_manager.py --set-priority manual dcf analyst
    echo "Done! Manual values will now be used as the primary fair value source."
    exit 0
fi

# Analyst targets first
if [ "$1" == "--analyst-first" ]; then
    echo "Setting analyst targets as primary fair value source..."
    python config_manager.py --set-priority analyst dcf manual
    echo "Done! Analyst targets will now be used as the primary fair value source."
    exit 0
fi

# Custom priority order
if [ "$1" == "--custom" ]; then
    if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
        echo "Error: Custom priority requires 3 sources to be specified."
        echo "Example: ./set_fair_value_priority.sh --custom dcf analyst manual"
        exit 1
    fi
    
    # Check that the sources are valid
    for source in "$2" "$3" "$4"; do
        if [[ ! "$source" =~ ^(dcf|manual|analyst)$ ]]; then
            echo "Error: Invalid source '$source'. Must be 'dcf', 'manual', or 'analyst'."
            exit 1
        fi
    done
    
    echo "Setting custom fair value priority..."
    python config_manager.py --set-priority "$2" "$3" "$4"
    echo "Done! Fair value priority set to: $2 (primary) → $3 → $4"
    exit 0
fi

# If we got here, the user provided an invalid option
echo "Error: Invalid option '$1'"
show_help
exit 1
