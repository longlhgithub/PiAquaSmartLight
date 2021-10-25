import asyncio
import sys
from bleak import BleakClient


address = "FF:FF:38:5C:1C:3F"

characteristic = "0000ffd9-0000-1000-8000-00805f9b34fb"

async def main(address):
    turnOn = False
    if len(sys.argv) >=2 and sys.argv[1] == 'on':
        turnOn = True
    print(turnOn)
    onOffCommand = bytes([-52 & 0xff, 35, 51])
    if not turnOn:
        onOffCommand = bytes([-52 & 0xff, 36, 51])
    
    client = BleakClient(address)
    try:
        await client.connect()
        result = await client.write_gatt_char(characteristic,onOffCommand,True)
        print("Result: {0}".format("".join(map(chr, result))))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

asyncio.run(main(address))