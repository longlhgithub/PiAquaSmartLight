import datetime
from math import ceil
from device import MyColor
from device import DeviceState
class TimeSlot:
    def __init__(self) -> None:
        self.color = MyColor()
        self.time = datetime.time()
    def __init__(self, color:MyColor, time:datetime.time) -> None:
        self.color = color
        self.time = time
    

    def __repr__(self) -> str:
        return f'<TimeSlot Color:{self.color}, Time: {self.time}>'
    

    def __eq__(self, o: object) -> bool:
        return isinstance(o,TimeSlot) and self.color == o.color and self.time == o.time

    def get_offset_color(self, other) -> MyColor:
        if not isinstance(other,TimeSlot):
            return None
        current_time = datetime.datetime.now().time()
        current_delta = datetime.timedelta(hours=current_time.hour,minutes = current_time.minute, seconds = current_time.second )
       
        next = self if self.time >other.time else other
        previous = self if next.time == other.time else other

        previous_delta = datetime.timedelta(hours=previous.time.hour,minutes = previous.time.minute, seconds = previous.time.second )
        next_delta = datetime.timedelta(hours=next.time.hour,minutes = next.time.minute, seconds = next.time.second )
        if current_time>= next.time:
            return next.color
        if previous.time< current_time < next.time:
            seconds_diff = (next_delta - previous_delta).total_seconds()
            if seconds_diff>0:
                remain_seconds = (next_delta - current_delta).total_seconds()
                time_ratio = remain_seconds/seconds_diff*100
                red = next.color.red -(next.color.red - previous.color.red)*time_ratio/100
                green = red = next.color.green -(next.color.green - previous.color.green)*time_ratio/100
                blue = next.color.blue -(next.color.blue - previous.color.blue)*time_ratio/100
                brightness = next.color.brightness -(next.color.brightness - previous.color.brightness)*time_ratio/100
                return MyColor(ceil(red),ceil(green),ceil(blue),ceil(brightness))
        
        return None
        
        

    