Installation
============

Requirements
------------

* Python 3.11 or higher
* Poetry (for development)

Installing from PyPI
--------------------

.. code-block:: bash

    pip install hydra-router

Development Installation
------------------------

1. Clone the repository:

.. code-block:: bash

    git clone <repository-url>
    cd hydra-router

2. Install Poetry if you haven't already:

.. code-block:: bash

    curl -sSL https://install.python-poetry.org | python3 -

3. Install dependencies:

.. code-block:: bash

    poetry install

4. Activate the virtual environment:

.. code-block:: bash

    poetry shell

Dependencies
------------

The main runtime dependency is:

* **pyzmq** (^25.0.0) - Python bindings for ZeroMQ

Development dependencies include testing, linting, and documentation tools.
