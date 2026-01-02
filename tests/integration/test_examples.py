"""
Integration tests for example files.

These tests run the actual example files to ensure they work correctly
and don't have import or runtime errors.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import AsyncGenerator, List

import pytest

from hydra_router.constants.DMsgType import DMsgType
from hydra_router.constants.DRouter import DRouter
from hydra_router.mq_client import MQClient, ZMQMessage
from hydra_router.router import HydraRouter


class TestExamples:
    """Test that example files run without errors."""

    @pytest.fixture  # type: ignore[misc]
    async def test_router(self) -> AsyncGenerator[HydraRouter, None]:
        """Start a test router for examples."""
        router = HydraRouter(
            router_address="127.0.0.1",
            router_port=5559,  # Different port for example tests
            client_timeout=10.0,
        )
        await router.start()
        yield router
        await router.shutdown()

    def get_example_files(self) -> List[Path]:
        """Get list of example files to test."""
        examples_dir = Path("examples")
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        example_files = []
        for file_path in examples_dir.glob("*.py"):
            if file_path.name != "__init__.py":
                example_files.append(file_path)

        return example_files

    async def test_example_imports(self) -> None:
        """Test that all examples can be imported without errors."""
        example_files = self.get_example_files()

        for example_file in example_files:
            # Test import by running python -c "import module"
            module_name = f"examples.{example_file.stem}"

            result = subprocess.run(
                [sys.executable, "-c", f"import {module_name}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"Failed to import {example_file.name}:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

    async def test_basic_usage_example(self) -> None:
        """Test basic_usage.py example."""
        result = subprocess.run(
            [sys.executable, "examples/basic_usage.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert result.returncode == 0, f"basic_usage.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Basic Usage Example" in result.stdout
        assert "Creating MQClient" in result.stdout

    async def test_configuration_example(self) -> None:
        """Test configuration_example.py example."""
        result = subprocess.run(
            [sys.executable, "examples/configuration_example.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert (
            result.returncode == 0
        ), f"configuration_example.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Configuration Example" in result.stdout

    async def test_error_handling_example(self) -> None:
        """Test error_handling.py example."""
        result = subprocess.run(
            [sys.executable, "examples/error_handling.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert result.returncode == 0, f"error_handling.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Error Handling Example" in result.stdout

    async def test_custom_client_type_example(self) -> None:
        """Test custom_client_type.py example."""
        result = subprocess.run(
            [sys.executable, "examples/custom_client_type.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert result.returncode == 0, f"custom_client_type.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Custom Client Type Example" in result.stdout

    async def test_multiple_clients_example(self) -> None:
        """Test multiple_clients.py example."""
        result = subprocess.run(
            [sys.executable, "examples/multiple_clients.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert result.returncode == 0, f"multiple_clients.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Multiple Clients Example" in result.stdout

    async def test_simple_square_demo_example(self) -> None:
        """Test simple_square_demo.py example."""
        result = subprocess.run(
            [sys.executable, "examples/simple_square_demo.py"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should run without errors
        assert result.returncode == 0, f"simple_square_demo.py failed:\n{result.stderr}"

        # Should contain expected output
        assert "Simple Square Demo" in result.stdout

    async def test_basic_client_server_with_router(
        self, test_router: HydraRouter
    ) -> None:
        """Test basic_client_server.py with a running router."""
        print("Testing basic client-server communication...")

        # Create server
        server = MQClient(
            router_address="tcp://127.0.0.1:5559",
            client_type=DRouter.SIMPLE_SERVER,
            client_id="test-server",
        )

        # Create client
        client = MQClient(
            router_address="tcp://127.0.0.1:5559",
            client_type=DRouter.SIMPLE_CLIENT,
            client_id="test-client",
        )

        responses_received = []

        def handle_square_request(message: ZMQMessage) -> None:
            print(f"SERVER RECEIVED REQUEST: {message}")
            data = message.data or {}
            number = data.get("number", 0)
            result = number * number

            response = ZMQMessage(
                message_type=DMsgType.SQUARE_RESPONSE,
                timestamp=time.time(),
                client_id="test-server",
                request_id=message.request_id,
                data={"number": number, "result": result},
            )

            print(f"SERVER SENDING RESPONSE: {response}")
            asyncio.create_task(server.send_message(response))

        def handle_square_response(message: ZMQMessage) -> None:
            print(f"CLIENT RECEIVED RESPONSE: {message}")
            responses_received.append(message)

        try:
            await server.connect()
            await client.connect()

            server.register_message_handler(
                DMsgType.SQUARE_REQUEST, handle_square_request
            )
            client.register_message_handler(
                DMsgType.SQUARE_RESPONSE, handle_square_response
            )

            # Start listening
            print("Waiting for connections to stabilize...")
            await asyncio.sleep(0.5)  # Let connections stabilize
            print("Connections stabilized")

            # Send request
            request = ZMQMessage(
                message_type=DMsgType.SQUARE_REQUEST,
                timestamp=time.time(),
                client_id="test-client",
                request_id="test-1",
                data={"number": 7},
            )

            print(f"CLIENT SENDING REQUEST: {request}")
            await client.send_message(request)
            print("Request sent, waiting for response...")
            await asyncio.sleep(3)  # Wait longer for response
            print("Wait complete")

            print(f"RESPONSES RECEIVED: {len(responses_received)}")
            for i, resp in enumerate(responses_received):
                print(f"Response {i}: {resp}")

            # Check results
            assert len(responses_received) == 1
            response = responses_received[0]
            assert response.data is not None
            assert response.data["number"] == 7
            assert response.data["result"] == 49

            print("✅ Basic client-server test passed!")

        finally:
            await server.disconnect()
            await client.disconnect()

        # Add a small delay to ensure router logs are captured
        await asyncio.sleep(0.1)

    async def test_all_examples_syntax_check(self) -> None:
        """Test that all examples have valid Python syntax."""
        example_files = self.get_example_files()

        for example_file in example_files:
            # Test syntax by compiling
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(example_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"Syntax error in {example_file.name}:\n" f"STDERR: {result.stderr}"
                )

    async def test_examples_have_required_imports(self) -> None:
        """Test that examples import required modules correctly."""
        example_files = self.get_example_files()

        required_imports = [
            "from hydra_router.constants.DMsgType import DMsgType",
            "from hydra_router.constants.DRouter import DRouter",
            "from hydra_router.mq_client import MQClient",
        ]

        for example_file in example_files:
            content = example_file.read_text()

            # Check for at least some required imports
            has_dmsgtype = "DMsgType" in content
            has_drouter = "DRouter" in content
            has_mqclient = "MQClient" in content

            if has_dmsgtype or has_drouter or has_mqclient:
                # If it uses these classes, it should import them correctly
                for required_import in required_imports:
                    if any(
                        cls in content for cls in ["DMsgType", "DRouter", "MQClient"]
                    ):
                        # At least one of the imports should be present
                        import_found = any(imp in content for imp in required_imports)
                        assert (
                            import_found
                        ), f"{example_file.name} uses hydra_router classes but missing proper imports"
