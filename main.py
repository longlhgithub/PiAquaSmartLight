from asyncio import tasks
from device import Device
import asyncio
d = Device()
async def handle_input():
    while True:
        user_input  = input('your CMD: ')
        if user_input == 'scan':
            await d.discover()
        elif user_input =='stop':
            await d.stop_discover()
        await asyncio.sleep(0.1)
async def main():
    await handle_input()

asyncio.run(main())