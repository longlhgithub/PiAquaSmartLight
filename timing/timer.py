from device.my_color import MyColor
from .time_slot import TimeSlot
import datetime
import yaml
class Timer:
    def __init__(self, **args) -> None:
        self.slots:list[TimeSlot] = []   
        self.enabled:bool = False
        settingFile = args.get('fromFile','')
        if not str.isspace(settingFile):
            self.load_settings(settingFile)
    

    def load_settings(self,file:str):
        with open(file,"r") as f:
            time_settings = yaml.safe_load(f)
            # print(time_settings)
            # slots = [x for x in time_settings['slots']] 
            for slot in time_settings['slots']:
                color = MyColor(slot['color'][0],slot['color'][1],slot['color'][2],slot['color'][3])
                time = datetime.time.fromisoformat(slot['time'])
                self.slots.append(TimeSlot(color,time))
            self.enabled = time_settings['enabled']


    def __str__(self) -> str:
        return f"Enabled: {self.enabled}, Slots: {self.slots}"
