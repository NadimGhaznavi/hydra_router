Installation Guide
==================

This guide covers installing HydraRouter in various environments.

System Requirements
-------------------

**Python Version**
   HydraRouter requires Python 3.11 or later.

**Operating Systems**
   - Linux (Ubuntu 20.04+, CentOS 8+, etc.)
   - macOS (10.15+)
   - Windows (10+)

**Dependencies**
   - ZeroMQ (pyzmq) - Core messaging library
   - asyncio - Asynchronous programming support
   - PyYAML - Configuration file support
   - psutil - System monitoring

Installation Methods
--------------------

PyPI Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install hydra-router

For system-wide installation:

.. code-block:: bash

   sudo pip install hydra-router

For user-only installation:

.. code-block:: bash

   pip install --user hydra-router

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Install from source for development:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/NadimGhaznavi/hydra_router.git
   cd hydra_router

   # Install in development mode
   pip install -e .

   # Install development dependencies
   pip install -e ".[dev]"

Docker Installation
~~~~~~~~~~~~~~~~~~~

Run HydraRouter in a Docker container:

.. code-block:: bash

   # Pull the official image
   docker pull hydra-router:latest

   # Run the router
   docker run -p 5556:5556 hydra-router:latest

   # Run with custom configuration
   docker run -p 5557:5557 hydra-router:latest \
       hydra-router start --address 0.0.0.0 --port 5557

Virtual Environment Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install in a virtual environment (recommended for development):

.. code-block:: bash

   # Create virtual environment
   python -m venv hydra-env

   # Activate virtual environment
   # On Linux/macOS:
   source hydra-env/bin/activate
   # On Windows:
   hydra-env\Scripts\activate

   # Install HydraRouter
   pip install hydra-router

Conda Installation
~~~~~~~~~~~~~~~~~~

Install using conda:

.. code-block:: bash

   # Create conda environment
   conda create -n hydra-router python=3.11

   # Activate environment
   conda activate hydra-router

   # Install from PyPI (conda package coming soon)
   pip install hydra-router

Verification
------------

Verify your installation:

.. code-block:: bash

   # Check version
   hydra-router --version

   # Test basic functionality
   python -c "from hydra_router import HydraRouter; print('Installation successful')"

   # Run help command
   hydra-router --help

Platform-Specific Instructions
------------------------------

Ubuntu/Debian
~~~~~~~~~~~~~~

.. code-block:: bash

   # Update package list
   sudo apt update

   # Install Python and pip
   sudo apt install python3.11 python3.11-pip python3.11-venv

   # Install system dependencies
   sudo apt install build-essential libzmq3-dev

   # Install HydraRouter
   pip3.11 install hydra-router

CentOS/RHEL/Fedora
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install Python and development tools
   sudo dnf install python3.11 python3.11-pip python3.11-devel
   sudo dnf groupinstall "Development Tools"

   # Install ZeroMQ
   sudo dnf install zeromq-devel

   # Install HydraRouter
   pip3.11 install hydra-router

macOS
~~~~~

.. code-block:: bash

   # Install Homebrew (if not already installed)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install Python
   brew install python@3.11

   # Install ZeroMQ
   brew install zeromq

   # Install HydraRouter
   pip3.11 install hydra-router

Windows
~~~~~~~

1. **Install Python**:
   - Download Python 3.11+ from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install Visual Studio Build Tools** (for compiling native dependencies):
   - Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "C++ build tools" workload

3. **Install HydraRouter**:

   .. code-block:: shell

      pip install hydra-router

Troubleshooting Installation
----------------------------

Common Issues
~~~~~~~~~~~~~

**"No module named 'zmq'"**
   ZeroMQ installation failed. Try:

   .. code-block:: bash

      # On Ubuntu/Debian
      sudo apt install libzmq3-dev

      # On macOS
      brew install zeromq

      # Then reinstall
      pip install --force-reinstall pyzmq

**"Microsoft Visual C++ 14.0 is required" (Windows)**
   Install Visual Studio Build Tools:

   .. code-block:: shell

      # Download and install from:
      # https://visualstudio.microsoft.com/visual-cpp-build-tools/

**"Permission denied" errors**
   Use virtual environment or user installation:

   .. code-block:: bash

      pip install --user hydra-router

**"Command 'hydra-router' not found"**
   Check if pip bin directory is in PATH:

   .. code-block:: bash

      # Add to ~/.bashrc or ~/.zshrc
      export PATH="$HOME/.local/bin:$PATH"

      # Or find the installation path
      python -m site --user-base

Upgrading
---------

Upgrade to Latest Version
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Upgrade from PyPI
   pip install --upgrade hydra-router

   # Check new version
   hydra-router --version

Downgrade to Specific Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install specific version
   pip install hydra-router==0.2.5

   # Or downgrade
   pip install --force-reinstall hydra-router==0.2.5

Uninstallation
--------------

Remove HydraRouter
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Uninstall package
   pip uninstall hydra-router

   # Remove configuration files (optional)
   rm -rf ~/.hydra-router/

   # Remove virtual environment (if used)
   rm -rf hydra-env/

Development Setup
-----------------

For Contributors
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone repository
   git clone https://github.com/NadimGhaznavi/hydra_router.git
   cd hydra_router

   # Create development environment
   python -m venv dev-env
   source dev-env/bin/activate  # On Windows: dev-env\Scripts\activate

   # Install in development mode with all dependencies
   pip install -e ".[dev,docs,viz,server,tui]"

   # Install pre-commit hooks
   pre-commit install

   # Run tests to verify setup
   pytest tests/

   # Build documentation
   cd docs && make html

Testing Installation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run unit tests
   pytest tests/unit/

   # Run integration tests
   pytest tests/integration/

   # Run all tests with coverage
   pytest tests/ --cov=hydra_router --cov-report=html

Next Steps
----------

After installation:

1. **Start the router**: ``hydra-router start``
2. **Read the getting started guide**: :doc:`getting_started`
3. **Try the examples**: :doc:`examples`
4. **Configure for your environment**: :doc:`configuration`

For production deployment, see :doc:`deployment`.
