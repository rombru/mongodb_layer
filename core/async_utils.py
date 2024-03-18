import asyncio
from threading import Thread


def create_loop():
    loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(loop,), daemon=True)
    t.start()
    return loop


def start_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def stop_loop(loop: asyncio.AbstractEventLoop):
    loop.stop()
