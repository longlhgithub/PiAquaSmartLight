
import asyncio
from bleak import exc
from message.command import Command
from device import HappyLightDevice
class MessageProcessor:
    def __init__(self,device_address) -> None:
        self.device = HappyLightDevice(device_address)
        # asyncio.ensure_future(self.device.connect())


    async def process(self,command:str):  
        try:      
            cmd = Command(command.lower())
            if not cmd.is_valid():
                print(f'CMD INVALID: {command}')
                return
            
            print(f'RECV CMD: {command}')
            args = cmd.get_arguments()
            c = cmd.get_command()
            if c == 'power':
                
                if len(args) != 1:
                    print('POWER CMD -> INVALID ARGS')
                else:
                    if args[0] == 'on':
                        await self.device.set_power(True)
                    else:
                        await self.device.set_power(False)
            elif c == 'color':
                if len(args) <3 or len(args)>4:
                    print('COLOR CMD -> INVALID ARGS')
                else:
                    r = int(args[0])
                    g = int(args[1])
                    b = int(args[2])
                    bright = self.device.state.brightness if len(args)==3 else int(args[3])
                    await self.device.set_color(red=r,green=g,blue = b, brightness=bright)

            else:
                print(f"UNSUPPORTED CMD -> {cmd.command}")
        except Exception as e:
            print(e)
