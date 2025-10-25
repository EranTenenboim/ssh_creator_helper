"""
Test configuration and fixtures for SSH Creator Helper
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    return {
        'username': 'testuser',
        'home': '/home/testuser',
        'uid': 1000,
        'gid': 1000
    }


@pytest.fixture
def mock_ssh_key():
    """Mock SSH key pair for testing"""
    return {
        'private_key': '-----BEGIN OPENSSH PRIVATE KEY-----\ntest_private_key\n-----END OPENSSH PRIVATE KEY-----',
        'public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqajDhA... testuser@hostname'
    }


@pytest.fixture
def mock_sshd_config():
    """Mock SSH daemon configuration"""
    return """# SSH Daemon Configuration
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# Authentication
LoginGraceTime 120
PermitRootLogin yes
StrictModes yes
MaxAuthTries 6
MaxSessions 10

# Key Authentication
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Password Authentication
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
"""


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b''
        mock_run.return_value.stderr = b''
        yield mock_run


@pytest.fixture
def mock_os_system():
    """Mock os.system calls"""
    with patch('os.system') as mock_system:
        mock_system.return_value = 0
        yield mock_system


@pytest.fixture
def mock_file_operations():
    """Mock file operations"""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.path.isfile') as mock_isfile, \
         patch('os.path.isdir') as mock_isdir, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.chmod') as mock_chmod, \
         patch('os.chown') as mock_chown:
        
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'isfile': mock_isfile,
            'isdir': mock_isdir,
            'makedirs': mock_makedirs,
            'chmod': mock_chmod,
            'chown': mock_chown
        }
