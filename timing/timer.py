from device.device import DeviceState
from device.my_color import MyColor
from .time_slot import TimeSlot
import datetime
import yaml
import asyncio


class Timer:
    def __init__(self, **args) -> None:
        self.slots: list[TimeSlot] = []
        self.enabled: bool = False
        settingFile = args.get('fromFile', '')
        self.device_state:DeviceState = None
        self.previous_color:MyColor = None
        self.on_next_color = None
        self.skip_minor_slot = False

        if not str.isspace(settingFile):
            self.load_settings(settingFile)
        self.next_slot = self.slots[0] if len(self.slots) else None



    async def run(self):
        while True:
            try:
                if len(self.slots)>0:
                    next_slot_indexes = [i for i,x in enumerate(self.slots) if x.time>datetime.datetime.now().time()]
                    if len(next_slot_indexes) ==0:                 
                        next_slot_indexes= [0]
                    next_slot = self.slots[next_slot_indexes[0]]
                    if next_slot != self.next_slot:
                        self.next_slot = next_slot
                        self.skip_minor_slot = False
                    self.previous_slot = self.slots[next_slot_indexes[0]-1]
                    new_color = self.previous_slot.get_offset_color(self.next_slot)
                    if new_color !=None and new_color!=self.previous_color and self.skip_minor_slot== False:
                        self.previous_color = new_color
                        if callable(self.on_next_color):
                            self.on_next_color(new_color)


                    # print(f'previous slot: {self.previous_slot}, next slot: {self.next_slot}')
                await asyncio.sleep(1)
            except Exception as e:
                print(f'timer.run EX: {e}')
            


    def load_settings(self, file: str):
        with open(file, "r") as f:
            time_settings = yaml.safe_load(f)
            print(time_settings)
            # slots = [x for x in time_settings['slots']]
            for slot in time_settings['slots']:
                color = MyColor(slot['color'][0], slot['color']
                                [1], slot['color'][2], slot['color'][3])
                time = datetime.time.fromisoformat(slot['time'])
                self.slots.append(TimeSlot(color, time))
            self.enabled = time_settings['enabled']
            self.slots.sort(key= lambda s : s.time)
            print(self.slots)

    def save_settings(self, file: str = 'settings.yaml'):
        data = {"slots": [], "enabled": self.enabled}
        
        for slot in self.slots:
            slot_data = {}
            slot_data['color'] = [slot.color.red, slot.color.green,
                                  slot.color.blue, slot.color.brightness]
            slot_data['time'] = slot.time.isoformat()
            data['slots'].append(slot_data)
        with open(file,'w') as stream:
            yaml.dump(data,stream)

    def __str__(self) -> str:
        return f"Enabled: {self.enabled}, Slots: {self.slots}"
