#!/bin/bash

# Define Tool Version
VERSION="1.3.0"

# Get the absolute path of manage.sh directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo "Usage: ./manage.sh [OPTIONS]"
    echo ""
    echo "A CLI tool manager for Raspberry Pi & FastAPI development."
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message and exit"
    echo "  -v, --version  Show version information and exit"
    echo ""
    echo "If no options are provided, the interactive CLI menu will launch."
}

show_version() {
    echo "Development Tools CLI Manager v${VERSION}"
}

show_menu() {
    clear
    echo "========================================="
    echo "    🛠️  DevTools CLI Manager v${VERSION} 🛠️"
    echo "========================================="
    echo "1) 🚀 Initialize Pi (IoT Core) Project"
    echo "2) 🌐 Initialize Pi (IoT + Web Portal) Project"
    echo "3) 📦 Generate Customized Module Block"
    echo "q) ❌ Exit"
    echo "========================================="
}

# Check CLI Arguments
if [ "$1" != "" ]; then
    case $1 in
        -h | --help ) show_help; exit 0 ;;
        -v | --version ) show_version; exit 0 ;;
        * ) echo "Error: Unknown option '$1'"; show_help; exit 1 ;;
    esac
fi

# Interactive Menu Loop
while true; do
    show_menu
    read -p "Select an option: " choice

    case $choice in
        1)
            echo ""
            read -p "Enter target directory path (Default: current directory): " target_path
            target_path="${target_path:-.}"
            bash "$SCRIPT_DIR/scripts/init_pi_iot/init_pi_iot.sh" "$target_path"
            echo ""
            read -p "Press any key to return to menu..."
            ;;
        2)
            echo ""
            read -p "Enter target directory path (Default: current directory): " target_path
            target_path="${target_path:-.}"
            bash "$SCRIPT_DIR/scripts/init_pi_web/init_pi_web.sh" "$target_path"
            echo ""
            read -p "Press any key to return to menu..."
            ;;
        3)
            echo ""
            read -p "Enter base path for the new module (Default: current directory): " base_path
            base_path="${base_path:-.}"
            read -p "Enter your custom module name (e.g., gpio_control): " module_name
            if [ -z "$module_name" ]; then
                echo "⚠️  Module name cannot be empty!"
            else
                bash "$SCRIPT_DIR/scripts/generate_module/generate_module.sh" "$base_path" "$module_name"
            fi
            echo ""
            read -p "Press any key to return to menu..."
            ;;
        [Qq])
            echo -e "\n👋 Exiting DevTools. Happy coding!"
            exit 0
            ;;
        *)
            echo -e "\n⚠️  Invalid option, please try again."
            sleep 1.5
            ;;
    esac
done