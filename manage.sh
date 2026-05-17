#!/bin/bash

# Define Tool Version
VERSION="1.0.1"

# Get the absolute path of manage.sh directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to display help usage
show_help() {
	echo "Usage: ./manage.sh [OPTIONS]"
	echo ""
	echo "A CLI tool manager for Raspberry Pi development."
	echo ""
	echo "Options:"
	echo "  -h, --help     Show this help message and exit"
	echo "  -v, --version  Show version information and exit"
	echo ""
	echo "If no options are provided, the interactive CLI menu will launch."
}

# Function to display version
show_version() {
	echo "Development Tools CLI Manager v${VERSION}"
}

# Function to display the interactive menu
show_menu() {
	clear
	echo "========================================="
	echo "    🛠️  DevTools CLI Manager v${VERSION} 🛠️"
	echo "========================================="
	echo "1) 🚀 Initialize Pi Project"
	echo "2) 🔄 Reserved for Future Tools"
	echo "q) ❌ Exit"
	echo "========================================="
}

# Check CLI Arguments
if [ "$1" != "" ]; then
	case $1 in
	-h | --help)
		show_help
		exit 0
		;;
	-v | --version)
		show_version
		exit 0
		;;
	*)
		echo "Error: Unknown option '$1'"
		show_help
		exit 1
		;;
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
		# Use current directory if input is empty
		target_path="${target_path:-.}"

		# 💡 這裡已更新為新的子目錄與新腳本名稱
		bash "$SCRIPT_DIR/scripts/init_pi_project/init_pi_project.sh" "$target_path"

		echo ""
		read -p "Press any key to return to menu..."
		;;
	2)
		echo -e "\nℹ️  This feature is not implemented yet!"
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
