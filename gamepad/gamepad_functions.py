import evdev
import pprint
import time
import asyncio

running = True

async def listen_00(dev):
    global running
    async for ev in dev.async_read_loop():
        print("00:",evdev.categorize(ev))
        if ev.code == evdev.ecodes.BTN_MODE and ev.value == 0:
            running = False
            break


async def listen_01(dev):
    while running:
        r = dev.absinfo(evdev.ecodes.ABS_X).value
        print("01:",r)
        await asyncio.sleep(0.05)


async def main():
    found_gamepad = False
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 'X-Box' in device.name:
            found_gamepad = True
            break
    if found_gamepad: 
        gamepad = evdev.InputDevice(device.path) # type: ignore
    else :
        raise RuntimeError(f"Failed to initialize gamepad.")
    gamepad_str = pprint.pformat(gamepad.capabilities(verbose=True))
    print(gamepad_str)

    L = await asyncio.gather(
        listen_00(gamepad),
        listen_01(gamepad))

asyncio.run(main())