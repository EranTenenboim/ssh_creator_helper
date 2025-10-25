#!/bin/bash

# SSH Authentication Management Script
# This script provides a menu to:
# 1. Create a new SSH key pair
# 2. Configure SSH server to use only key-based authentication
# 3. Revert SSH server to allow password authentication

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if script is run with sudo/root privileges
check_privileges() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}This script must be run as root or with sudo privileges.${NC}"
        echo -e "Please run: ${YELLOW}sudo $0${NC}"
        exit 1
    fi
}

# Function to create SSH key
create_ssh_key() {
    clear
    echo -e "${BLUE}=== Create SSH Key Pair ===${NC}"
    echo
    
    # Ask for username
    read -rp "Enter the username to create the key for: " username
    
    # Verify user exists
    if ! id "$username" &>/dev/null; then
        echo -e "${RED}Error: User '$username' does not exist.${NC}"
        return 1
    fi
    
    # Get user's home directory
    user_home=$(eval echo ~"$username")
    
    # Ask for key name
    read -rp "Enter a name for the key (default: id_rsa): " key_name
    key_name=${key_name:-id_rsa}
    
    # Check if key already exists
    if [ -f "$user_home/.ssh/$key_name" ]; then
        echo -e "${YELLOW}Warning: A key with name '$key_name' already exists.${NC}"
        read -rp "Do you want to overwrite it? (y/n): " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Key creation aborted.${NC}"
            return 1
        fi
    fi
    
    # Create .ssh directory if it doesn't exist
    if [ ! -d "$user_home/.ssh" ]; then
        mkdir -p "$user_home/.ssh"
        chmod 700 "$user_home/.ssh"
        chown "$username":"$username" "$user_home/.ssh"
    fi
    
    # Generate the key
    echo -e "${GREEN}Generating SSH key pair...${NC}"
    if sudo -u "$username" ssh-keygen -t rsa -b 4096 -f "$user_home/.ssh/$key_name" -N ""; then
        echo -e "${GREEN}SSH key pair created successfully!${NC}"
        echo -e "Private key: ${YELLOW}$user_home/.ssh/$key_name${NC}"
        echo -e "Public key: ${YELLOW}$user_home/.ssh/$key_name.pub${NC}"
        
        # Set correct permissions
        chmod 600 "$user_home/.ssh/$key_name"
        chmod 644 "$user_home/.ssh/$key_name.pub"
        chown "$username":"$username" "$user_home/.ssh/$key_name"
        chown "$username":"$username" "$user_home/.ssh/$key_name.pub"
        
        # Add to authorized_keys if not already there
        authorized_keys_file="$user_home/.ssh/authorized_keys"
        if [ ! -f "$authorized_keys_file" ]; then
            touch "$authorized_keys_file"
            chmod 600 "$authorized_keys_file"
            chown "$username":"$username" "$authorized_keys_file"
        fi
        
        cat "$user_home/.ssh/$key_name.pub" >> "$authorized_keys_file"
        echo -e "${GREEN}Public key added to authorized_keys.${NC}"
        
        # Ask if user wants to export the private key as PEM
        read -rp "Do you want to export the private key as a .pem file? (y/n): " export_pem
        if [[ $export_pem =~ ^[Yy]$ ]]; then
            pem_file="$user_home/$key_name.pem"
            cp "$user_home/.ssh/$key_name" "$pem_file"
            chmod 600 "$pem_file"
            chown "$username":"$username" "$pem_file"
            echo -e "${GREEN}Private key exported as PEM file: ${YELLOW}$pem_file${NC}"
        fi
    else
        echo -e "${RED}Failed to create SSH key pair.${NC}"
        return 1
    fi
    
    echo
    read -rp "Press Enter to continue..."
    return 0
}

# Function to configure SSH server to use only key authentication
force_key_auth() {
    clear
    echo -e "${BLUE}=== Configure SSH Server to Use Only Key Authentication ===${NC}"
    echo
    
    sshd_config="/etc/ssh/sshd_config"
    
    # Backup the original config file
    backup_file="$sshd_config.backup.$(date +%Y%m%d%H%M%S)"
    cp "$sshd_config" "$backup_file"
    echo -e "${GREEN}SSH config file backed up to: ${YELLOW}$backup_file${NC}"
    
    # Make the necessary changes
    echo -e "${YELLOW}Modifying SSH server configuration...${NC}"
    
    # Function to update sshd_config setting
    update_setting() {
        setting="$1"
        value="$2"
        
        # Check if setting already exists
        if grep -q "^#*\s*$setting" "$sshd_config"; then
            # Comment out existing setting and add new one
            sed -i "s/^#*\s*$setting.*/#&/" "$sshd_config"
            echo "$setting $value" >> "$sshd_config"
        else
            # Add setting if it doesn't exist
            echo "$setting $value" >> "$sshd_config"
        fi
    }
    
    update_setting "PasswordAuthentication" "no"
    update_setting "PubkeyAuthentication" "yes"
    update_setting "ChallengeResponseAuthentication" "no"
    update_setting "UsePAM" "yes"
    
    echo -e "${GREEN}SSH configuration updated!${NC}"
    echo -e "${YELLOW}Changes made:${NC}"
    echo "  - Disabled password authentication"
    echo "  - Enabled public key authentication"
    echo "  - Disabled challenge-response authentication"
    
    # Restart SSH service
    echo -e "${YELLOW}Restarting SSH service...${NC}"
    
    # Check which init system is in use
    if command -v systemctl &>/dev/null; then
        systemctl restart sshd
    elif command -v service &>/dev/null; then
        service sshd restart
    else
        /etc/init.d/ssh restart
    fi
    
    if systemctl restart sshd; then
        echo -e "${GREEN}SSH service restarted successfully!${NC}"
        echo -e "${YELLOW}IMPORTANT: Keep your SSH session open and test key-based login in a new session before closing this one.${NC}"
    else
        echo -e "${RED}Failed to restart SSH service. Please check the configuration.${NC}"
        echo -e "${YELLOW}It is recommended to restore the backup: ${YELLOW}cp $backup_file $sshd_config${NC}"
    fi
    
    echo
    read -rp "Press Enter to continue..."
    return 0
}

# Function to test SSH connection with PEM key
test_ssh_connection() {
    clear
    echo -e "${BLUE}=== Test SSH Connection with PEM Key ===${NC}"
    echo
    
    # Ask for server details
    read -rp "Enter the server IP address or hostname: " server
    read -rp "Enter the username: " username
    read -rp "Enter the path to the PEM key file: " pem_file
    read -rp "Enter the SSH port (default: 22): " ssh_port
    ssh_port=${ssh_port:-22}
    
    # Validate inputs
    if [ -z "$server" ] || [ -z "$username" ] || [ -z "$pem_file" ]; then
        echo -e "${RED}Error: All fields are required.${NC}"
        echo
        read -rp "Press Enter to continue..."
        return 1
    fi
    
    # Validate SSH port
    if ! [[ "$ssh_port" =~ ^[0-9]+$ ]] || [ "$ssh_port" -lt 1 ] || [ "$ssh_port" -gt 65535 ]; then
        echo -e "${RED}Error: SSH port must be a number between 1 and 65535.${NC}"
        echo
        read -rp "Press Enter to continue..."
        return 1
    fi
    
    # Check if PEM file exists
    if [ ! -f "$pem_file" ]; then
        echo -e "${RED}Error: PEM file '$pem_file' does not exist.${NC}"
        echo
        read -rp "Press Enter to continue..."
        return 1
    fi
    
    # Check PEM file permissions
    pem_perms=$(stat -c "%a" "$pem_file" 2>/dev/null)
    if [ "$pem_perms" != "600" ] && [ "$pem_perms" != "400" ]; then
        echo -e "${YELLOW}Warning: PEM file permissions are not secure (current: $pem_perms).${NC}"
        echo -e "${YELLOW}Recommended permissions: 600 or 400${NC}"
        read -rp "Do you want to continue anyway? (y/n): " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Test aborted.${NC}"
            echo
            read -rp "Press Enter to continue..."
            return 1
        fi
    fi
    
    # Test SSH connection
    echo -e "${GREEN}Testing SSH connection...${NC}"
    echo -e "${YELLOW}Command: ssh -i \"$pem_file\" -p $ssh_port -o ConnectTimeout=10 -o BatchMode=yes $username@$server 'echo \"SSH connection successful!\"'${NC}"
    echo
    
    # Perform the test
    if ssh -i "$pem_file" -p "$ssh_port" -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no "$username@$server" 'echo "SSH connection successful!"' 2>&1; then
        echo
        echo -e "${GREEN}✓ SSH connection test PASSED!${NC}"
        echo -e "${GREEN}The PEM key is working correctly.${NC}"
    else
        echo
        echo -e "${RED}✗ SSH connection test FAILED!${NC}"
        echo -e "${YELLOW}Possible issues:${NC}"
        echo "  - PEM key file is incorrect or corrupted"
        echo "  - Username is incorrect"
        echo "  - Server is not accessible"
        echo "  - SSH service is not running on the server"
        echo "  - Firewall is blocking the connection"
        echo "  - Public key is not in the server's authorized_keys"
    fi
    
    echo
    read -rp "Press Enter to continue..."
    return 0
}

# Function to revert SSH server to allow password authentication
allow_password_auth() {
    clear
    echo -e "${BLUE}=== Revert SSH Server to Allow Password Authentication ===${NC}"
    echo
    
    sshd_config="/etc/ssh/sshd_config"
    
    # Backup the original config file
    backup_file="$sshd_config.backup.$(date +%Y%m%d%H%M%S)"
    cp "$sshd_config" "$backup_file"
    echo -e "${GREEN}SSH config file backed up to: ${YELLOW}$backup_file${NC}"
    
    # Make the necessary changes
    echo -e "${YELLOW}Modifying SSH server configuration...${NC}"
    
    # Function to update sshd_config setting
    update_setting() {
        setting="$1"
        value="$2"
        
        # Check if setting already exists
        if grep -q "^#*\s*$setting" "$sshd_config"; then
            # Comment out existing setting and add new one
            sed -i "s/^#*\s*$setting.*/#&/" "$sshd_config"
            echo "$setting $value" >> "$sshd_config"
        else
            # Add setting if it doesn't exist
            echo "$setting $value" >> "$sshd_config"
        fi
    }
    
    update_setting "PasswordAuthentication" "yes"
    update_setting "PubkeyAuthentication" "yes"
    update_setting "ChallengeResponseAuthentication" "yes"
    update_setting "UsePAM" "yes"
    
    echo -e "${GREEN}SSH configuration updated!${NC}"
    echo -e "${YELLOW}Changes made:${NC}"
    echo "  - Enabled password authentication"
    echo "  - Public key authentication remains enabled"
    echo "  - Enabled challenge-response authentication"
    
    # Restart SSH service
    echo -e "${YELLOW}Restarting SSH service...${NC}"
    
    # Check which init system is in use
    if command -v systemctl &>/dev/null; then
        systemctl restart sshd
    elif command -v service &>/dev/null; then
        service sshd restart
    else
        /etc/init.d/ssh restart
    fi
    
    if systemctl restart sshd; then
        echo -e "${GREEN}SSH service restarted successfully!${NC}"
        echo -e "${YELLOW}Password authentication is now enabled.${NC}"
    else
        echo -e "${RED}Failed to restart SSH service. Please check the configuration.${NC}"
        echo -e "${YELLOW}It is recommended to restore the backup: ${YELLOW}cp $backup_file $sshd_config${NC}"
    fi
    
    echo
    read -rp "Press Enter to continue..."
    return 0
}

# Main menu function
show_menu() {
    clear
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}    SSH Authentication Manager    ${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
    echo -e "${YELLOW}1.${NC} Create SSH Key Pair (PEM)"
    echo -e "${YELLOW}2.${NC} Force SSH to Use Only Key Authentication"
    echo -e "${YELLOW}3.${NC} Revert to Password Authentication"
    echo -e "${YELLOW}4.${NC} Test SSH Connection with PEM Key"
    echo -e "${YELLOW}5.${NC} Exit"
    echo
    echo -e "${BLUE}=====================================${NC}"
    echo
    read -rp "Enter your choice [1-5]: " choice
    
    case $choice in
        1) create_ssh_key ;;
        2) force_key_auth ;;
        3) allow_password_auth ;;
        4) test_ssh_connection ;;
        5) exit 0 ;;
        *) echo -e "${RED}Invalid choice. Please try again.${NC}"
           sleep 2
           ;;
    esac
}

# Main function
main() {
    # Check for root privileges
    check_privileges
    
    # Show menu in a loop
    while true; do
        show_menu
    done
}

# Run the main function
main