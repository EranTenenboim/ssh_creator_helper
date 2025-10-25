"""
Test suite for SSH Authentication Manager
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
import subprocess


class TestSSHAuthManager:
    """Test class for SSH Authentication Manager functionality"""
    
    def test_check_privileges_root(self):
        """Test privilege check with root user"""
        with patch('os.getuid', return_value=0):
            # Import here to avoid issues with the script execution
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            
            # Mock the script execution
            with patch('sys.argv', ['ssh_auth_manager.sh']):
                # This would normally exit, but we'll test the logic
                from ssh_auth_manager import check_privileges
                # Should not raise an exception for root user
                try:
                    check_privileges()
                except SystemExit:
                    pytest.fail("check_privileges() should not exit for root user")
    
    def test_check_privileges_non_root(self):
        """Test privilege check with non-root user"""
        with patch('os.getuid', return_value=1000):
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            
            with patch('sys.argv', ['ssh_auth_manager.sh']):
                from ssh_auth_manager import check_privileges
                with pytest.raises(SystemExit) as exc_info:
                    check_privileges()
                assert exc_info.value.code == 1
    
    def test_create_ssh_key_validation(self, temp_dir, mock_user):
        """Test SSH key creation validation"""
        # Create test environment
        test_home = os.path.join(temp_dir, 'home', mock_user['username'])
        os.makedirs(test_home, exist_ok=True)
        
        with patch('id') as mock_id, \
             patch('eval') as mock_eval, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chmod') as mock_chmod, \
             patch('os.chown') as mock_chown, \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.exists', return_value=False):
            
            mock_id.return_value = True
            mock_eval.return_value = test_home
            mock_run.return_value.returncode = 0
            
            # Test user validation
            with patch('builtins.input', side_effect=['nonexistent_user']):
                import sys
                sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from ssh_auth_manager import create_ssh_key
                
                # Mock id to return False for nonexistent user
                with patch('id', return_value=False):
                    result = create_ssh_key()
                    assert result == 1  # Should return error code
    
    def test_ssh_key_creation_success(self, temp_dir, mock_user, mock_ssh_key):
        """Test successful SSH key creation"""
        test_home = os.path.join(temp_dir, 'home', mock_user['username'])
        os.makedirs(test_home, exist_ok=True)
        
        with patch('id') as mock_id, \
             patch('eval') as mock_eval, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chmod') as mock_chmod, \
             patch('os.chown') as mock_chown, \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.input', side_effect=[mock_user['username'], 'test_key', 'y']):
            
            mock_id.return_value = True
            mock_eval.return_value = test_home
            mock_run.return_value.returncode = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import create_ssh_key
            
            result = create_ssh_key()
            assert result == 0  # Should return success
    
    def test_force_key_auth_configuration(self, mock_sshd_config):
        """Test SSH configuration for key-only authentication"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_sshd_config)) as mock_file, \
             patch('subprocess.run') as mock_run, \
             patch('os.system') as mock_system:
            
            mock_run.return_value.returncode = 0
            mock_system.return_value = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import force_key_auth
            
            with patch('builtins.input', return_value=''):
                result = force_key_auth()
                assert result == 0
    
    def test_allow_password_auth_configuration(self, mock_sshd_config):
        """Test SSH configuration to allow password authentication"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_sshd_config)) as mock_file, \
             patch('subprocess.run') as mock_run, \
             patch('os.system') as mock_system:
            
            mock_run.return_value.returncode = 0
            mock_system.return_value = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import allow_password_auth
            
            with patch('builtins.input', return_value=''):
                result = allow_password_auth()
                assert result == 0
    
    def test_ssh_connection_test_success(self, temp_dir):
        """Test successful SSH connection test"""
        pem_file = os.path.join(temp_dir, 'test_key.pem')
        
        # Create a mock PEM file
        with open(pem_file, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest_key\n-----END OPENSSH PRIVATE KEY-----")
        
        with patch('subprocess.run') as mock_run:
            # Mock successful SSH connection
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'SSH connection successful!'
            mock_run.return_value.stderr = b''
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import test_ssh_connection
            
            with patch('builtins.input', side_effect=['192.168.1.1', 'testuser', pem_file]):
                result = test_ssh_connection()
                assert result == 0
    
    def test_ssh_connection_test_failure(self, temp_dir):
        """Test failed SSH connection test"""
        pem_file = os.path.join(temp_dir, 'test_key.pem')
        
        # Create a mock PEM file
        with open(pem_file, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest_key\n-----END OPENSSH PRIVATE KEY-----")
        
        with patch('subprocess.run') as mock_run:
            # Mock failed SSH connection
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = b''
            mock_run.return_value.stderr = b'Permission denied'
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import test_ssh_connection
            
            with patch('builtins.input', side_effect=['192.168.1.1', 'testuser', pem_file]):
                result = test_ssh_connection()
                assert result == 0  # Function should still return 0, but connection fails
    
    def test_ssh_connection_test_invalid_pem(self, temp_dir):
        """Test SSH connection with invalid PEM file"""
        with patch('os.path.exists', return_value=False):
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import test_ssh_connection
            
            with patch('builtins.input', side_effect=['192.168.1.1', 'testuser', '/nonexistent/pem']):
                result = test_ssh_connection()
                assert result == 1  # Should return error code
    
    def test_ssh_connection_test_invalid_permissions(self, temp_dir):
        """Test SSH connection with insecure PEM permissions"""
        pem_file = os.path.join(temp_dir, 'test_key.pem')
        
        # Create a mock PEM file
        with open(pem_file, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest_key\n-----END OPENSSH PRIVATE KEY-----")
        
        with patch('os.stat') as mock_stat, \
             patch('subprocess.run') as mock_run:
            
            # Mock insecure permissions (755)
            mock_stat.return_value.st_mode = 0o755
            mock_run.return_value.returncode = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import test_ssh_connection
            
            with patch('builtins.input', side_effect=['192.168.1.1', 'testuser', pem_file, 'n']):
                result = test_ssh_connection()
                assert result == 1  # Should return error code due to user declining
    
    def test_menu_display(self):
        """Test menu display functionality"""
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from ssh_auth_manager import show_menu
        
        with patch('builtins.input', return_value='5'), \
             patch('sys.exit') as mock_exit:
            
            show_menu()
            mock_exit.assert_called_once_with(0)
    
    def test_menu_invalid_choice(self):
        """Test menu with invalid choice"""
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from ssh_auth_manager import show_menu
        
        with patch('builtins.input', return_value='99'), \
             patch('time.sleep') as mock_sleep:
            
            # This should not exit, just show error and continue
            show_menu()
            mock_sleep.assert_called_once_with(2)


class TestSSHSecurity:
    """Test security aspects of SSH operations"""
    
    def test_pem_file_permissions_validation(self, temp_dir):
        """Test PEM file permission validation"""
        pem_file = os.path.join(temp_dir, 'test_key.pem')
        
        # Create a mock PEM file
        with open(pem_file, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest_key\n-----END OPENSSH PRIVATE KEY-----")
        
        # Test with secure permissions
        with patch('os.stat') as mock_stat:
            mock_stat.return_value.st_mode = 0o600  # Secure permissions
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import test_ssh_connection
            
            with patch('builtins.input', side_effect=['192.168.1.1', 'testuser', pem_file]):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value.returncode = 0
                    result = test_ssh_connection()
                    assert result == 0
    
    def test_ssh_key_permissions_setting(self, temp_dir, mock_user):
        """Test that SSH keys are created with correct permissions"""
        test_home = os.path.join(temp_dir, 'home', mock_user['username'])
        os.makedirs(test_home, exist_ok=True)
        
        with patch('id') as mock_id, \
             patch('eval') as mock_eval, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chmod') as mock_chmod, \
             patch('os.chown') as mock_chown, \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.input', side_effect=[mock_user['username'], 'test_key', 'y']):
            
            mock_id.return_value = True
            mock_eval.return_value = test_home
            mock_run.return_value.returncode = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import create_ssh_key
            
            create_ssh_key()
            
            # Verify that chmod was called with correct permissions
            mock_chmod.assert_any_call(os.path.join(test_home, '.ssh', 'test_key'), 0o600)
            mock_chmod.assert_any_call(os.path.join(test_home, '.ssh', 'test_key.pub'), 0o644)


class TestSSHIntegration:
    """Integration tests for SSH operations"""
    
    def test_complete_ssh_workflow(self, temp_dir, mock_user, mock_ssh_key):
        """Test complete SSH key creation and testing workflow"""
        test_home = os.path.join(temp_dir, 'home', mock_user['username'])
        os.makedirs(test_home, exist_ok=True)
        pem_file = os.path.join(temp_dir, 'test_key.pem')
        
        # Create a mock PEM file
        with open(pem_file, 'w') as f:
            f.write(mock_ssh_key['private_key'])
        
        with patch('id') as mock_id, \
             patch('eval') as mock_eval, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chmod') as mock_chmod, \
             patch('os.chown') as mock_chown, \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.input', side_effect=[mock_user['username'], 'test_key', 'y']):
            
            mock_id.return_value = True
            mock_eval.return_value = test_home
            mock_run.return_value.returncode = 0
            
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ssh_auth_manager import create_ssh_key
            
            # Test key creation
            result = create_ssh_key()
            assert result == 0
            
            # Test SSH connection with created key
            with patch('os.stat') as mock_stat, \
                 patch('subprocess.run') as mock_ssh_run:
                
                mock_stat.return_value.st_mode = 0o600
                mock_ssh_run.return_value.returncode = 0
                
                from ssh_auth_manager import test_ssh_connection
                
                with patch('builtins.input', side_effect=['192.168.1.1', mock_user['username'], pem_file]):
                    result = test_ssh_connection()
                    assert result == 0
