Installation
============

Requirements
------------

* Python 3.11 or higher
* Poetry (for development)

Pre-Requisite
-------------

Create a virtual environment.

.. code-block:: bash

    python3 -m venv hydra_venv
    . hydra_venv/bin/activate


Installing from PyPI
--------------------

.. code-block:: bash

    pip install hydra-router

Dependencies
------------

The main runtime dependency is:

* **pyzmq** (^25.0.0) - Python bindings for ZeroMQ

Development dependencies include testing, linting, and documentation tools.
