Architecture
============

Hydra Router follows an abstract base class pattern:

* **HydraClient**: Abstract base class for all client implementations
* **HydraClientPing**: Concrete ping client that sends structured ping messages
* **HydraServer**: Abstract base class for all server implementations  
* **HydraServerPong**: Concrete pong server that responds to ping messages

All communication uses the HydraMsg protocol for structured, reliable messaging between 
components.