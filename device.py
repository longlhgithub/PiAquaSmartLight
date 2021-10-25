from bleak import BleakScanner
class Device:
    def __init__(self) -> None:
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)
        
    def detection_callback(self, device, advertisement_data):
         print(device.address, "RSSI:", device.rssi, advertisement_data)
    async def discover(self):      
        await self.scanner.start()
    async def stop_discover(self):
        await self.scanner.stop()