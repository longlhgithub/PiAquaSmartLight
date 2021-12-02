import asyncio
import os
import signal
import time
import gmqtt
import yaml
# import uvloop

from gmqtt import Client 
RPC_COMMAND_TOPIC = 'MQTTnet.RPC/+/'
class MQTTClient:
    STOP = asyncio.Event()
    def __init__(self,host,port,username,password,on_message, cmd_topic="aqualight/cmd") -> None:
        self.host = host
        self.port = port
        self.username= username
        self.password = password
        self.cmd_topic = cmd_topic
        self.device_type = 0
        self.client_id= '123456'
        self.client = Client(self.client_id,will_message=gmqtt.Message(f'device/0/{self.client_id}/lwt','i died'))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe    
        if self.username:    
            self.client.set_auth_credentials(self.username, self.password)
        self.on_message_callback = on_message

    async def connect(self):
        print(f'connecting to {self.host}')
        await self.client.connect(self.host,port=self.port)


    async def disconnect(self):
        await MQTTClient.STOP.wait()
        await self.client.disconnect() 

    def subscribe(self, topic):
        self.client.subscribe(topic,qos=0)
    async def publish(self, message):
        self.client.publish('test', str(time.time()), qos=1)

    def on_connect(self, client, flags, rc, properties):
        print('MQTT connected')
        print(f'subscribing to {self.cmd_topic}')
        print(f'{RPC_COMMAND_TOPIC}{self.client_id}.cmd')
        # client.subscribe(self.cmd_topic, qos=0)
        client.subscribe(f'{RPC_COMMAND_TOPIC}{self.client_id}.cmd')
        if callable(self.on_connected):
             self.on_connected(client)


    def on_message(self, client, topic, payload:bytes, qos, properties):
        print('RECV MSG:', payload)
                 
        self.on_message_callback(payload.decode('utf-8'),topic)



    def on_disconnect(self, client, packet, exc=None):
        print('MQTT disconnected')

    def on_subscribe(self, client, mid, qos, properties):
        print('SUBSCRIBED')

    def ask_exit(self, *args):
        MQTTClient.STOP.set()
    
    def publish_state(self,payload):
        self.client.publish(f'device/{self.device_type}/{self.client_id}/telemetry',payload)
    
async def main(client:MQTTClient):
    await client.connect();
   
    # await client.publish('test');
    # client.subscribe('ttt/#')
    while True:
        await asyncio.sleep(5)
    
if __name__ == '__main__':
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # loop = asyncio.get_event_loop()

    # Read YAML file
    with open("settings.yaml", 'r') as stream:
        settings = yaml.safe_load(stream)
    client = MQTTClient(settings['mqtt']['server_url'],settings['mqtt']['username'],settings['mqtt']['password'])
    

    # loop.add_signal_handler(signal.SIGINT,client.ask_exit)
    # loop.add_signal_handler(signal.SIGTERM, client.ask_exit)

    # loop.run_until_complete(main(client))
    asyncio.run(main(client))