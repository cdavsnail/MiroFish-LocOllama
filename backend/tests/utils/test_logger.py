import os
import sys
import logging
import pytest
from unittest.mock import patch, MagicMock
from logging.handlers import RotatingFileHandler

# Import the module to be tested
from app.utils.logger import (
    setup_logger,
    get_logger,
    _ensure_utf8_stdout,
    LOG_DIR,
    debug,
    info,
    warning,
    error,
    critical,
    logger as default_logger,
)


@pytest.fixture(autouse=True)
def clean_loggers():
    """Fixture to ensure loggers are cleaned up after each test."""
    yield
    # Cleanup handlers for the default test loggers to ensure test isolation
    for name in ['test_logger', 'new_test_logger', 'mirofish']:
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()


def test_ensure_utf8_stdout(monkeypatch):
    """Test standard output encoding configuration on Windows."""
    # Mock sys.platform to simulate Windows
    monkeypatch.setattr(sys, 'platform', 'win32')

    # Create mock objects for sys.stdout and sys.stderr with a reconfigure method
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()

    monkeypatch.setattr(sys, 'stdout', mock_stdout)
    monkeypatch.setattr(sys, 'stderr', mock_stderr)

    _ensure_utf8_stdout()

    mock_stdout.reconfigure.assert_called_once_with(encoding='utf-8', errors='replace')
    mock_stderr.reconfigure.assert_called_once_with(encoding='utf-8', errors='replace')


def test_ensure_utf8_stdout_non_win32(monkeypatch):
    """Test that stdout/stderr are not reconfigured on non-Windows platforms."""
    # Mock sys.platform to simulate Linux
    monkeypatch.setattr(sys, 'platform', 'linux')

    mock_stdout = MagicMock()
    monkeypatch.setattr(sys, 'stdout', mock_stdout)

    _ensure_utf8_stdout()

    mock_stdout.reconfigure.assert_not_called()


def test_setup_logger_creates_directory():
    """Test that setup_logger creates the log directory if it doesn't exist."""
    with patch('os.makedirs') as mock_makedirs:
        setup_logger('test_logger')
        mock_makedirs.assert_called_once_with(LOG_DIR, exist_ok=True)


def test_setup_logger_handlers():
    """Test that setup_logger adds the correct handlers."""
    logger = setup_logger('test_logger')

    # Should have 2 handlers: RotatingFileHandler and StreamHandler
    assert len(logger.handlers) == 2

    has_file_handler = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
    has_stream_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    assert has_file_handler
    assert has_stream_handler

    # Check propagate flag
    assert not logger.propagate

    # Check levels
    file_handler = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))
    # Note: StreamHandler is a base class of RotatingFileHandler, so we need to exclude RotatingFileHandler
    stream_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler))

    assert file_handler.level == logging.DEBUG
    assert stream_handler.level == logging.INFO


def test_setup_logger_idempotent():
    """Test that setup_logger does not add duplicate handlers if called multiple times."""
    logger1 = setup_logger('test_logger')
    assert len(logger1.handlers) == 2

    # Call again
    logger2 = setup_logger('test_logger')
    assert logger1 is logger2
    # Still only 2 handlers, no duplicates
    assert len(logger2.handlers) == 2


def test_get_logger_existing():
    """Test get_logger returns an existing logger with handlers."""
    # Set up first
    setup_logger('test_logger')

    # Use patch to verify setup_logger is not called
    with patch('app.utils.logger.setup_logger') as mock_setup:
        logger = get_logger('test_logger')
        mock_setup.assert_not_called()
        assert len(logger.handlers) == 2


def test_get_logger_new():
    """Test get_logger creates a new logger if handlers don't exist."""
    # Ensure it's a new logger with no handlers
    logging.getLogger('new_test_logger').handlers.clear()

    with patch('app.utils.logger.setup_logger') as mock_setup:
        mock_logger = MagicMock()
        mock_setup.return_value = mock_logger

        result = get_logger('new_test_logger')

        mock_setup.assert_called_once_with('new_test_logger')
        assert result is mock_logger


def test_convenience_methods():
    """Test the convenience methods delegate to the default logger."""
    with patch.object(default_logger, 'debug') as mock_debug, \
         patch.object(default_logger, 'info') as mock_info, \
         patch.object(default_logger, 'warning') as mock_warning, \
         patch.object(default_logger, 'error') as mock_error, \
         patch.object(default_logger, 'critical') as mock_critical:

        debug("test debug", 1, a=2)
        mock_debug.assert_called_once_with("test debug", 1, a=2)

        info("test info")
        mock_info.assert_called_once_with("test info")

        warning("test warning")
        mock_warning.assert_called_once_with("test warning")

        error("test error")
        mock_error.assert_called_once_with("test error")

        critical("test critical")
        mock_critical.assert_called_once_with("test critical")
