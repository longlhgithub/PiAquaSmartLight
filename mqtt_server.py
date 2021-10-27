import asyncio
from config import settings
from mqtt import MQTTClient
from message import MessageProcessor

print(settings)
message_processor = MessageProcessor(settings['pair_device'][0]['address'])
def on_message(payload):
    print('MSG:', payload)
    # asyncio.create_task(message_processor.process(payload))
    asyncio.ensure_future(message_processor.process(payload))
    

mqtt_client = MQTTClient(settings['mqtt']['server_url'],settings['mqtt']['username'],settings['mqtt']['password'],on_message)
mqtt_client.on_message = on_message

async def main():
    await mqtt_client.connect()
    while True:
        await asyncio.sleep(5)

asyncio.run(main())

