import datetime
from device import MyColor
class TimeSlot:
    def __init__(self) -> None:
        self.color = MyColor()
        self.time = datetime.time()
    def __init__(self, color:MyColor, time:datetime.time) -> None:
        self.color = color
        self.time = time
    

    def __repr__(self) -> str:
        return f'<TimeSlot Color:{self.color}, Time: {self.time}>'

    def __getattribute__(self, name: str) -> list:
        return {'color':self.color.__getattribute__()}]