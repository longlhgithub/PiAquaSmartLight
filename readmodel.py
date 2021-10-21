
import asyncio
from bleak import BleakClient

address = "ff:ff:38:5c:1c:3f"
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

asyncio.run(main(address))