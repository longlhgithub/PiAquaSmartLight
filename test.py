import asyncio
from bleak import BleakClient

address = "FF:FF:38:5C:1C:3F"
MODEL_NBR_UUID = "0000ffd9-0000-1000-8000-00805f9b34fb"

async def main(address):
    async with BleakClient(address) as client:
        data = bytes([-17 & 0xff, 1, 119]) #get light data
        #data = bytes([36, 42, 43, 66]) # get time data
        read_light_data = await client.write_gatt_char(MODEL_NBR_UUID,data)
        await asyncio.sleep(2)
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        int_values = [x for x in model_number]

        print("Model Number: {0}".format(int_values))
        

asyncio.run(main(address))