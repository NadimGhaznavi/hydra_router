"""Test basic package structure and imports."""

import hydra_router


class TestPackageStructure:
    """Test that the package structure is correct."""

    def test_package_version(self) -> None:
        """Test that package has correct version."""
        assert hydra_router.__version__ == "0.3.8"

    def test_package_author(self) -> None:
        """Test that package has correct author."""
        assert hydra_router.__author__ == "Nadim-Daniel Ghaznavi"

    def test_main_components_importable(self) -> None:
        """Test that main components can be imported."""
        from hydra_router import HydraRouter, MQClient, RouterConstants

        # These are placeholder classes for now
        assert RouterConstants is not None
        assert MQClient is not None
        assert HydraRouter is not None

    def test_entry_point_modules_exist(self) -> None:
        """Test that entry point modules exist."""
        import hydra_router.router
        import hydra_router.simple_client
        import hydra_router.simple_server

        assert hasattr(hydra_router.router, "main")
        assert hasattr(hydra_router.simple_client, "main")
        assert hasattr(hydra_router.simple_server, "main")
