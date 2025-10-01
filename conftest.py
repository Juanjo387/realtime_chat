"""
Pytest configuration and fixtures.
"""
import pytest
from django.conf import settings
import os

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up database for tests."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_chatdb',
        'USER': os.getenv('DB_USER', 'chatuser'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'chatpassword'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass 