
from bleak import exc
from message.command import Command
from device import HappyLightDevice
class MessageProcessor:
    def __init__(self,device_address) -> None:
        self.device = HappyLightDevice(device_address)


    async def process(self,command:str):  
        try:      
            cmd = Command(command.lower())
            if not cmd.is_valid():
                print(f'CMD INVALID: {command}')
                return
            
            print(f'RECV CMD: {command}')

            if cmd.get_command() == 'power':
                args = cmd.get_arguments()
                if len(args) != 1:
                    print('POWER CMD -> INVALID ARGS')
                else:
                    if args[0] == 'on':
                        await self.device.set_power(True)
                    else:
                        await self.device.set_power(False)
            else:
                print(f"UNSUPPORTED CMD -> {cmd.command}")
        except Exception as e:
            print(e)
