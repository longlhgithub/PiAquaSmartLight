from asyncio import tasks
from device import HappyLightDevice
import asyncio
d = HappyLightDevice()
async def handle_input():
    while True:
        user_input  = input('your CMD: ')
        if user_input == 'scan':
            await d.discover()
        elif user_input =='stop':
            await d.stop_discover()
        await asyncio.sleep(0.1)
async def main():
    # await handle_input()
    await d.discover()
    # while True:
    await asyncio.sleep(15)
    for t in d.scanner.discovered_devices:
        print(t)


asyncio.run(main())