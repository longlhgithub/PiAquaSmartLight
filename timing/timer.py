from device.my_color import MyColor
from .time_slot import TimeSlot
import datetime
import yaml


class Timer:
    def __init__(self, **args) -> None:
        self.slots: list[TimeSlot] = []
        self.enabled: bool = False
        settingFile = args.get('fromFile', '')
        if not str.isspace(settingFile):
            self.load_settings(settingFile)

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
