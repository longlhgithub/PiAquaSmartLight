from device.my_color import MyColor
import json
class DeviceState:
    def __init__(self) -> None:
        # self.red = 255
        # self.green = 255
        # self.blue = 255
        # elf.brightness = 255
        self.color = MyColor(0,0,0,0)
        self.brightness = 0
        self.power_state = False
        self.timer_settings ={}

    def __str__(self):
        power = 'ON' if self.power_state else 'OFF'
        return f"Power: {power}, COLOR({self.color}), Brightness: {self.brightness}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DeviceState):
            return NotImplemented
        return self.color == o.color and self.power_state == o.power_state

    def set_state(self, color: MyColor=None, power_state:bool=None, brightness:int=None, timer_settings=None):
        if color !=None:
            self.color = color
        if power_state != None:
            self.power_state = power_state
        if brightness!=None:
            self.brightness =brightness
        if timer_settings!=None:
            self.timer_settings = timer_settings
        if callable(self.on_state_changed):
            print(f'device state changed: {self}')
            self.on_state_changed(self)
        
    def to_json(self):
        res = {
            "power": self.power_state,
            "color": self.color.to_object(),
            "brightness": self.brightness,
            "timer": self.timer_settings
        }
        return json.dumps(res)
