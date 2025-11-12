"""Test basic package import functionality."""

def test_package_can_be_imported():
    """Test that the main package can be imported."""
    import mcp_server_atlassian
    assert mcp_server_atlassian is not None


def test_package_has_version():
    """Test that the package has a version attribute."""
    import mcp_server_atlassian
    assert hasattr(mcp_server_atlassian, '__version__')
    assert isinstance(mcp_server_atlassian.__version__, str)
    assert len(mcp_server_atlassian.__version__) > 0
