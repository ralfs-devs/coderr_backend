"""Testing configuration settings for the core project.

Overrides the primary database setup with an in-memory SQLite configuration 
and optimizes performance by using a faster password hasher for testing.
"""

from .settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
