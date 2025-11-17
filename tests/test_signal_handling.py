"""Tests for signal handling functionality."""

import signal
import pytest

from src.mcp_server_atlassian.signal import SignalHandler


class TestSignalHandler:
    """Test cases for SignalHandler context manager."""

    def test_context_manager_protocol(self):
        """Test SignalHandler can be used as context manager."""
        with SignalHandler() as handler:
            assert handler is not None
            assert isinstance(handler, SignalHandler)

    def test_signal_handlers_installed(self):
        """Test signal handlers are properly installed."""
        # Get original handlers
        original_sigint = signal.signal(signal.SIGINT, signal.SIG_DFL)
        original_sigpipe = signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        # Restore them
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGPIPE, original_sigpipe)

        with SignalHandler():
            # Check handlers are different during context
            current_sigint = signal.signal(signal.SIGINT, signal.SIG_DFL)
            current_sigpipe = signal.signal(signal.SIGPIPE, signal.SIG_DFL)

            # Restore for comparison
            signal.signal(signal.SIGINT, current_sigint)
            signal.signal(signal.SIGPIPE, current_sigpipe)

            assert current_sigint != original_sigint
            assert current_sigpipe != original_sigpipe

    def test_signal_handlers_restored(self):
        """Test original signal handlers are restored after context."""
        # Get original handlers
        original_sigint = signal.signal(signal.SIGINT, signal.SIG_DFL)
        original_sigpipe = signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        # Restore them
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGPIPE, original_sigpipe)

        with SignalHandler():
            pass

        # Check handlers are restored
        restored_sigint = signal.signal(signal.SIGINT, signal.SIG_DFL)
        restored_sigpipe = signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        # Restore for cleanup
        signal.signal(signal.SIGINT, restored_sigint)
        signal.signal(signal.SIGPIPE, restored_sigpipe)

        assert restored_sigint == original_sigint
        assert restored_sigpipe == original_sigpipe

    def test_sigint_handling(self, capfd):
        """Test SIGINT raises KeyboardInterrupt and logs warning."""
        with pytest.raises(SystemExit) as exc_info:
            with SignalHandler():
                # Let KeyboardInterrupt propagate to __exit__
                raise KeyboardInterrupt()

        # Check exit code is correct
        assert exc_info.value.code == 130

        # Check warning was logged to stderr
        captured = capfd.readouterr()
        assert "MCP server interrupted by SIGINT" in captured.err

    def test_sigpipe_handling(self):
        """Test SIGPIPE raises BrokenPipeError and exits silently."""
        with pytest.raises(SystemExit) as exc_info:
            with SignalHandler():
                # Let BrokenPipeError propagate to __exit__
                raise BrokenPipeError()

        # Check exit code is correct
        assert exc_info.value.code == 141

    def test_other_exceptions_not_suppressed(self):
        """Test other exceptions are not suppressed by context manager."""
        with pytest.raises(ValueError):
            with SignalHandler():
                raise ValueError("Test exception")

    def test_signal_handler_methods(self):
        """Test signal handler methods raise correct exceptions."""
        handler = SignalHandler()

        with pytest.raises(KeyboardInterrupt):
            handler._handle_sigint(signal.SIGINT, None)

        with pytest.raises(BrokenPipeError):
            handler._handle_sigpipe(signal.SIGPIPE, None)

    def test_no_exception_no_exit(self):
        """Test normal execution doesn't trigger exit."""
        with SignalHandler():
            # Normal execution
            pass

        # Should complete normally without any exit
