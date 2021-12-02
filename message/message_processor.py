
import asyncio
from datetime import time
import json
from bleak import exc
from message.command import Command
from device import HappyLightDevice
from timing.timer import Timer


class MessageProcessor:
    def __init__(self, device_address) -> None:
        self.timer: Timer = None
        self.device = HappyLightDevice(device_address)
        # asyncio.ensure_future(self.device.connect())

    def pause_timer(self):
        if self.timer != None and self.timer.skip_minor_slot == False:
            self.timer.skip_minor_slot = True

    async def process(self, command: str, topic: str):
        try:
            if topic.startswith('MQTTnet.RPC/'):
                print(f'RPC call: {command}')
                responseTopic = f'{topic}/response'
                self.mqtt_client.client.publish(responseTopic, '', qos=0)
                command_obj = json.loads(command)
                for k in command_obj:
                    command = k.lower()
                    if command == "color":
                        command = command + ' ' + ' '.join([str(x) for x in  command_obj[k]])
                    elif command =='timer':
                        command = command +' placeholder'
                    else:
                        command = k + ' ' + str(command_obj[k])
                    if(command.startswith('timer')):
                        cmd = Command(command)
                        cmd.command_fragment[1] = command_obj[k]
                        await self.execute_command(cmd)
                    else:
                        await self.execute_command(Command(command))
                return

            cmd = Command(command.lower())
            await self.execute_command(cmd)

        except Exception as e:
            print(f'ERROR: {e}')

    async def execute_command(self, command: Command):
        if not command.is_valid():
            print(f'CMD INVALID: {command}')
            return
        print(f'Exec CMD: {command.command}')
        args = command.get_arguments()
        c = command.get_command()
        if c == 'ping':
            await self.device.sync_data()
            self.device.state.set_state(timer_settings=self.timer.to_object())
        elif c=='timer':
            arg = args[0]
            self.timer.load_settings_from_object(arg)
            self.timer.skip_minor_slot= False
            self.timer.save_settings()
            self.timer.init()
            # print(arg)
        elif c == 'power':

            if len(args) != 1:
                print('POWER CMD -> INVALID ARGS')
            else:
                if args[0] == 'on' or args[0] == 'True':
                    await self.device.set_power_slowly(True)
                else:
                    await self.device.set_power_slowly(False)
                self.pause_timer()
        elif c == 'color':
            if len(args) < 3 or len(args) > 4:
                print('COLOR CMD -> INVALID ARGS')
            else:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                bright = self.device.state.brightness if len(
                    args) == 3 else int(args[3])
                await self.device.set_rgb_color(red=r, green=g, blue=b, brightness=bright)
                self.pause_timer()
        elif c == 'brightness':
            r = self.device.state.color.red
            g = self.device.state.color.green
            b = self.device.state.color.blue
            bright = self.device.state.brightness if len(
                args) != 1 else int(args[0])
            await self.device.set_rgb_color(red=r, green=g, blue=b, brightness=bright)

        else:
            print(f"UNSUPPORTED CMD -> {command.command}")
