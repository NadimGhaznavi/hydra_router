Architecture
============

Hydra Router follows an abstract base class pattern:

* **HydraClient**: Example class for all client implementations
* **HydraServer**: Example class for all server implementations
* **HydraRouter**: Concrete pong server that responds to ping messages

All communication uses the HydraMsg protocol for structured, reliable messaging between
components. HydraMQ provides a wrapper for ZeroMQ that hides the ZeroMQ complexity
and code.
