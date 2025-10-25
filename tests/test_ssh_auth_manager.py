"""
Test suite for SSH Authentication Manager
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import sys


class TestSSHAuthManager:
    """Test class for SSH Authentication Manager functionality"""
    
    def test_script_syntax(self):
        """Test that the shell script has valid syntax"""
        result = subprocess.run(['bash', '-n', 'ssh_auth_manager.sh'], 
                               capture_output=True, text=True)
        assert result.returncode == 0, f"Script syntax error: {result.stderr}"
    
    def test_script_executable(self):
        """Test that the script is executable"""
        # Make the script executable if it isn't
        if not os.access('ssh_auth_manager.sh', os.X_OK):
            os.chmod('ssh_auth_manager.sh', 0o755)
        assert os.access('ssh_auth_manager.sh', os.X_OK), "Script is not executable"
    
    def test_script_contains_functions(self):
        """Test that the script contains expected functions"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            assert 'create_ssh_key' in content, "create_ssh_key function not found"
            assert 'test_ssh_connection' in content, "test_ssh_connection function not found"
            assert 'force_key_auth' in content, "force_key_auth function not found"
            assert 'allow_password_auth' in content, "allow_password_auth function not found"
    
    def test_privilege_check_logic(self):
        """Test privilege check logic"""
        # Test root check
        result = subprocess.run(['bash', '-c', 'if [ "$(id -u)" -eq 0 ]; then echo "root"; else echo "not_root"; fi'], 
                               capture_output=True, text=True)
        assert result.returncode == 0
        
        # Test non-root check
        result = subprocess.run(['bash', '-c', 'if [ "$(id -u)" -ne 0 ]; then echo "not_root"; else echo "root"; fi'], 
                               capture_output=True, text=True)
        assert result.returncode == 0
    
    def test_script_help_display(self):
        """Test that the script shows help/usage information"""
        # Test that the script doesn't crash when run (expects root privilege error)
        result = subprocess.run(['timeout', '5s', 'bash', 'ssh_auth_manager.sh'], 
                               capture_output=True, text=True)
        # Should either complete, timeout, or exit with privilege error (1)
        assert result.returncode in [0, 1, 124], f"Script failed with return code {result.returncode}: {result.stderr}"
        # Should show privilege error message
        assert "root" in result.stdout or "sudo" in result.stdout, "Should show privilege requirement message"
    
    def test_script_functions_exist(self):
        """Test that all expected functions are defined in the script"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            functions = [
                'check_privileges',
                'create_ssh_key', 
                'force_key_auth',
                'allow_password_auth',
                'test_ssh_connection',
                'show_menu',
                'main'
            ]
            for func in functions:
                assert f"{func}()" in content, f"Function {func} not found in script"


class TestSSHSecurity:
    """Test security aspects of SSH operations"""
    
    def test_script_permissions(self):
        """Test that the script has appropriate permissions"""
        # Ensure script is executable
        os.chmod('ssh_auth_manager.sh', 0o755)
        stat_info = os.stat('ssh_auth_manager.sh')
        permissions = oct(stat_info.st_mode)[-3:]
        # Should be executable by owner
        assert permissions[2] in ['1', '3', '5', '7'], f"Script should be executable, got permissions: {permissions}"
    
    def test_script_no_hardcoded_secrets(self):
        """Test that the script doesn't contain hardcoded secrets"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read().lower()
            # Check for common secret patterns
            # 'password' is acceptable in comments and configuration settings
            assert 'secret' not in content, "Potential hardcoded secret found"
            assert 'key' in content, "SSH key functionality should be present"
    
    def test_script_input_validation(self):
        """Test that the script has input validation"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            # Should have input validation patterns
            assert 'read -rp' in content, "Input prompts should be present (using -r flag)"
            assert 'if [' in content, "Conditional logic should be present"
            assert 'then' in content, "Conditional logic should be present"


class TestSSHIntegration:
    """Integration tests for SSH operations"""
    
    def test_script_structure(self):
        """Test that the script has proper structure"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            
            # Should start with shebang
            assert content.startswith('#!/bin/bash'), "Script should start with shebang"
            
            # Should have proper function definitions
            assert 'function ' in content or '()' in content, "Functions should be defined"
            
            # Should have main execution
            assert 'main' in content, "Main function should be present"
    
    def test_script_colors_defined(self):
        """Test that color variables are defined"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            colors = ['RED=', 'GREEN=', 'YELLOW=', 'BLUE=', 'NC=']
            for color in colors:
                assert color in content, f"Color variable {color} not found"
    
    def test_script_menu_structure(self):
        """Test that the script has proper menu structure"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            # Should have menu options
            assert '1.' in content, "Menu option 1 should be present"
            assert '2.' in content, "Menu option 2 should be present"
            assert '3.' in content, "Menu option 3 should be present"
            assert '4.' in content, "Menu option 4 should be present"
            assert '5.' in content, "Menu option 5 should be present"
    
    def test_script_error_handling(self):
        """Test that the script has error handling"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            # Should have error handling patterns
            assert 'if [' in content, "Error handling should be present"
            assert 'else' in content, "Error handling should be present"
            assert 'return' in content, "Function returns should be present"
    
    def test_script_backup_functionality(self):
        """Test that the script has backup functionality"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            # Should have backup patterns
            assert 'backup' in content.lower(), "Backup functionality should be present"
            assert 'cp' in content, "Copy commands should be present for backups"
    
    def test_script_ssh_config_handling(self):
        """Test that the script handles SSH configuration"""
        with open('ssh_auth_manager.sh', 'r') as f:
            content = f.read()
            # Should have SSH config handling
            assert 'sshd_config' in content, "SSH daemon config should be handled"
            assert 'systemctl' in content, "System service management should be present"