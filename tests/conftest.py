"""Pytest configuration and shared fixtures for hydra-router tests."""

import asyncio
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def router_address() -> str:
    """Provide default router address for testing."""
    return "tcp://localhost:5556"


@pytest.fixture
def test_client_id() -> str:
    """Provide default client ID for testing."""
    return "test-client-001"
