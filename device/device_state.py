from device.my_color import MyColor


class DeviceState:
    def __init__(self) -> None:
        # self.red = 255
        # self.green = 255
        # self.blue = 255
        # self.brightness = 255
        self.color = MyColor()
        self.power_state = False        
    def __str__(self):
        power = 'ON' if self.power_state else 'OFF'
        return f"Power: {power}, COLOR({self.color})"
    

    def __eq__(self, o: object) -> bool:
        if not isinstance(o,DeviceState):
            return NotImplemented
        return self.color == o.color and self.power_state == o.power_state  
    
    def set_state(self, color:MyColor):
        self.color = color
    
