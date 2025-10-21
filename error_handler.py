"""
Centralized error handling utility for sanitizing error messages
Ensures sensitive implementation details are not exposed to users
"""

import logging
from typing import Optional, Dict, Any
import traceback

# Configure logging for internal error tracking
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ErrorHandler:
    """Handles error sanitization and logging"""
    
    # Map of specific error patterns to user-friendly messages
    ERROR_MESSAGES = {
        'database': '❌ Unable to access data. Please try again later.',
        'connection': '❌ Connection issue. Please check your internet connection and try again.',
        'file_not_found': '❌ Required data not found. Please contact support.',
        'permission': '❌ Access denied. Please check your permissions.',
        'validation': '❌ Invalid input. Please check your entry and try again.',
        'calculation': '❌ Unable to complete calculation. Please verify your data.',
        'provider_not_found': '❌ Provider not found. Please check the provider code.',
        'data_processing': '❌ Unable to process data. Please try again.',
        'default': '❌ An error occurred. Please try again later.'
    }
    
    @classmethod
    def get_safe_error_message(cls, error: Exception, error_type: str = 'default') -> str:
        """
        Returns a sanitized error message for display to users
        
        Args:
            error: The exception that was raised
            error_type: Category of error for appropriate messaging
            
        Returns:
            A user-friendly error message without sensitive details
        """
        # Log the actual error details for debugging
        cls._log_error(error, error_type)
        
        # Return sanitized message
        return cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES['default'])
    
    @classmethod
    def _log_error(cls, error: Exception, error_type: str):
        """
        Logs detailed error information for debugging purposes
        
        Args:
            error: The exception to log
            error_type: Category of error
        """
        error_details = {
            'error_type': error_type,
            'error_class': error.__class__.__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }
        
        logging.error(f"Error occurred: {error_details}")
    
    @classmethod
    def handle_database_error(cls, error: Exception) -> str:
        """Handles database-specific errors"""
        return cls.get_safe_error_message(error, 'database')
    
    @classmethod
    def handle_connection_error(cls, error: Exception) -> str:
        """Handles connection-specific errors"""
        return cls.get_safe_error_message(error, 'connection')
    
    @classmethod
    def handle_file_error(cls, error: Exception) -> str:
        """Handles file-related errors"""
        if 'not found' in str(error).lower() or 'no such file' in str(error).lower():
            return cls.get_safe_error_message(error, 'file_not_found')
        return cls.get_safe_error_message(error, 'permission')
    
    @classmethod
    def handle_validation_error(cls, error: Exception) -> str:
        """Handles validation errors"""
        return cls.get_safe_error_message(error, 'validation')
    
    @classmethod
    def handle_calculation_error(cls, error: Exception) -> str:
        """Handles calculation/processing errors"""
        return cls.get_safe_error_message(error, 'calculation')
    
    @classmethod
    def handle_provider_error(cls, error: Exception) -> str:
        """Handles provider-related errors"""
        return cls.get_safe_error_message(error, 'provider_not_found')