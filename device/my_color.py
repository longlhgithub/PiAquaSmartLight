class MyColor:
    def __init__(self,red = 255, green = 255, blue=255, brightness=100) -> None:
        self.red = red
        self.green = green
        self.blue = blue
        self.brightness = brightness

    def __repr__(self) -> str:
        return f'<MyColor {self.red},{self.green},{self.blue},{self.brightness}>'