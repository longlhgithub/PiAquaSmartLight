import asyncio
import os
import signal
import time
import yaml
# import uvloop

from gmqtt import Client 
class MQTTClient:
    STOP = asyncio.Event()
    def __init__(self,host,username,password) -> None:
        self.host = host
        self.username= username
        self.password = password
        self.client = Client("client-py")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.set_auth_credentials(self.username, self.password)
       

       
       

    async def connect(self):
        print(f'connecting to {self.host}')
        await self.client.connect(self.host)


    async def disconnect(self):
        await MQTTClient.STOP.wait()
        await self.client.disconnect() 

    def subscribe(self, topic):
        self.client.subscribe(topic,qos=0)
    async def publish(self, message):
        self.client.publish('test', str(time.time()), qos=1)

    def on_connect(self, client, flags, rc, properties):
        print('Connected')
        # client.subscribe('ttt/#', qos=0)


    def on_message(self, client, topic, payload, qos, properties):
        print('RECV MSG:', payload)


    def on_disconnect(self, client, packet, exc=None):
        print('Disconnected')

    def on_subscribe(self, client, mid, qos, properties):
        print('SUBSCRIBED')

    def ask_exit(self, *args):
        MQTTClient.STOP.set()
    
async def main(client:MQTTClient):
    await client.connect();
   
    await client.publish('test');
    client.subscribe('ttt/#')
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