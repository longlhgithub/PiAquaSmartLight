import asyncio
from config import settings
from device.device_state import DeviceState
from device.my_color import MyColor
from mqtt import MQTTClient
from message import MessageProcessor
import mqtt
from timing.timer import Timer

print(settings)
def on_device_state_changed(state:DeviceState):
    s = state.to_json()
    print(f'on_device_state_changed: {s}')
    mqtt_client.publish_state(s)  
     
     
message_processor = MessageProcessor(settings['pair_device'][0]['address'])
message_processor.device.state.on_state_changed = on_device_state_changed
     
      
def on_mqtt_connected (client:MQTTClient):
    if message_processor.device.client.is_connected:
        mqtt_client.publish_state(message_processor.device.state.to_json())   
def on_message(payload,topic):
    print('MSG:', payload)   
    # asyncio.create_task(message_processor.process(payload))
    asyncio.ensure_future(message_processor.process(payload,topic))

def on_timer_triggered(color:MyColor):
    print(f'on_timer_triggered: {color}')
    asyncio.ensure_future(trigger_light_by_timer(color))    

async def trigger_light_by_timer(color:MyColor):
    if color.brightness>=3 and not message_processor.device.state.power_state:
        await message_processor.device.set_color(color)
        await message_processor.device.set_power_slowly(True)
    elif color.brightness<3 and message_processor.device.state.power_state:   
        await message_processor.device.set_power_slowly(False)
    else:
        await message_processor.device.set_color(color)

mqtt_client = MQTTClient(settings['mqtt']['server_url'],settings['mqtt']['port'],settings['mqtt']['username'],settings['mqtt']['password'],on_message)
mqtt_client.on_message = on_message
mqtt_client.on_connected = on_mqtt_connected



async def main():
    try:
        timer = Timer(fromFile='timer_settings.yaml')
        message_processor.timer = timer
        timer.on_next_color  = on_timer_triggered
        task = asyncio.create_task(message_processor.device.connect());
        task2 = asyncio.create_task(mqtt_client.connect())
        task3 = asyncio.create_task(timer.run())
        message_processor.mqtt_client = mqtt_client;
        while True:
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print('stopped by user')
        await task.cancel()
        await task2.cancel()
        await task3.cancel()
        if message_processor.device.client.is_connected:
            await message_processor.device.client.disconnect()
        if mqtt_client.client.is_connected:
            await mqtt_client.client.disconnect()
    except Exception as e:
        print(f'EX: {e}')
asyncio.run(main())

