from hydra_router.utils.HydraMQ import HydraMQ
from hydra_router.utils.HydraMsg import HydraMsg


def main():
    # Create client
    mq = HydraMQ(
        router_address="localhost",
        router_port=5757,
        id="my-service"
    )

    # Send message (clean API)
    msg = HydraMsg(
        sender=mq.identity,
        target="other-service",
        method="ping",
        payload={"sequence": 1}
    )
    await mq.send(msg)

    # Receive message (returns HydraMsg, not raw bytes)
    response = await mq.recv()
    print(f"Got response: {response.method}")
    print(f"Payload: {response.payload}")

main()