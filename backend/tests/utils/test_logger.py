import logging
import uuid
from unittest.mock import MagicMock, patch

from app.utils.logger import Logger, get_logger


def test_get_logger_basic():
    """
    Basic test to verify we get a logger instance back, behavior regarding handlers
    depends on environment (pytest injects handlers).
    """
    name = f"TestLogger_{uuid.uuid4()}"
    logger = get_logger(name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == name
    assert logger.hasHandlers()


def test_logger_initialization_logic():
    """
    Test specifically that we add a handler if none exist (mocking hasHandlers=False).
    This ensures coverage of the setup logic.
    """
    with patch("app.utils.logger.logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock(spec=logging.Logger)
        # Simulate no handlers
        mock_logger.hasHandlers.return_value = False
        mock_logger.handlers = []

        mock_get_logger.return_value = mock_logger

        # Call function
        result = get_logger("MockedLogger")

        # Verify result
        assert result == mock_logger

        # Verify logic
        mock_logger.setLevel.assert_called_with(logging.DEBUG)
        mock_logger.addHandler.assert_called()

        # Verify we added a StreamHandler
        args, _ = mock_logger.addHandler.call_args
        handler = args[0]
        assert isinstance(handler, logging.StreamHandler)


def test_logger_class_direct():
    name = f"NewLogger_{uuid.uuid4()}"
    logger = Logger.get_logger(name)
    assert isinstance(logger, logging.Logger)
