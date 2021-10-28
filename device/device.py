import asyncio
from bleak import BleakClient
import math
class DeviceState:
    def __init__(self) -> None:
        self.red = 255
        self.green = 255
        self.blue = 255
        self.brightness = 255
        self.power_state = False
    def __str__(self):
        power = 'ON' if self.power_state else 'OFF'
        return f"Power: {power}, RGB({self.red},{self.green},{self.blue}), Brightness: {self.brightness}"
    
    def set_state(self,red,green,blue,brightness):
        self.red = red
        self.green = green
        self.blue = blue
        self.brightness = brightness


class HappyLightDevice:
    CONSMART_BLE_180a_UUID = "0000180a-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_2a25_UUID = "00002a25-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_DATA_UUID = "0000ffd4-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_MUSICCHECK_UUID = "0000fff4-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_MUSICMOD_UUID = "0000fff9-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_TIME_UUID = "0000fff7-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID = "0000ffd9-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_SERVICE_DATA_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_NOTIFICATION_SERVICE_WRGB_UUID = "0000ffd5-0000-1000-8000-00805f9b34fb";
    CONSMART_BLE_WRITE_CHARACTERISTICS_MUSICCHECK_UUID = "0000fff3-0000-1000-8000-00805f9b34fb";
    # public static final int SLIC_BLE_MANUFACTURER_DATA_LEN = 4;
    SLIC_BLE_NOTIFICATION_CHARACTERISTICS_SIGNAL_UUID = "00002a06-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_NOTIFICATION_SERVICE_SIGNAL_UUID = "00001803-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_DEVICE_INFO_MANUFACTURER_NAME_UUID = "00002a29-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_INFO_ADDRESS_UUID = "00002a03-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_INFO_APPEARANCE_UUID = "00002a01-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_INFO_DEVICE_NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_CHARACTERISTICS_TX_POWER_LEVEL_UUID = "00002a07-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_SERVICE_BATTERY_UUID = "0000180f-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_SERVICE_DEVICE_INFO_UUID = "0000180a-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_SERVICE_INFO_UUID = "00001800-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_READ_SERVICE_TX_POWER_LEVEL_UUID = "00001804-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_WRITE_CHARACTERISTICS_SOUND_ALERT_UUID = "00002a06-0000-1000-8000-00805f9b34fb";
    SLIC_BLE_WRITE_SERVICE_SOUND_ALERT_HIGH_UUID = "00001802-0000-1000-8000-00805f9b34fb";
    SWITCH_CAMERA_FIND_CHARA = "0000ffd1-0000-1000-8000-00805f9b34fb";
    SWITCH_CAMERA_FIND_SERVICE = "0000ffd0-0000-1000-8000-00805f9b34fb";
    SWITCH_FLIGHTMODE = "0000ffd3-0000-1000-8000-00805f9b34fb";

    def __init__(self,address:str) -> None:
        self.is_first_connected = True
        self.address = address      
        self.client = BleakClient(address)  
        self.client.set_disconnected_callback(self.on_disconnected)
        self.state = DeviceState()
        
        
    
    def on_disconnected(self, client):
        print(f'device {self.address} is disconnected')

    async def connect(self) -> bool:        
        if not self.client.is_connected:
            print(f'connecting to HappyLightDevice at {self.address}')
            is_connected = await self.client.connect()
            print(f'is_connected: {is_connected}, client.is_connected: {self.client.is_connected}')
            if self.client.is_connected:
                if  self.is_first_connected:
                    self.is_first_connected = False
                    
                print('set notify to Data')
                await self.client.start_notify(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_DATA_UUID,self.on_recv_data)
                print('got notified')
                await self.sync_data()
               
                # await self.client.start_notify(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,self.on_recv_wrgb_data)
                # above unsupported 
            return is_connected

        else:
            return True
    def on_recv_data(self,characteristic,data):
        self.process_data(data)
        int_values = [x for x in data]
        print(f'RECV DATA: {int_values} FROM {characteristic}')


    def process_data(self, data:bytearray):
        #[102, 4, 35, 65, 32, 15, 25, 22, 22, 0, 3, 153]
        # sync time 
        #(byte) (value[3] & 255), (byte) (value[5] & 255), (byte) (value[6] & 255), (byte) (value[7] & 255), (byte) (value[8] & 255), (byte) (255 & value[9])
        # 65 15 25 22 22 0
        #TODO sync time
        if len(data) == 12 and data[0] & 0xff == 102: # light data
            if data[2] == 35: # light is on
                self.state.power_state = True
            elif data[2] == 36: # light is off
                self.state.power_state = False
            red = data[6] & 255;
            green = data[7] & 255;
            blue = data[8] & 255;            
            brightness_ratio = float(255) / float(max(red,green,blue))
            self.state.brightness = math.floor(float(max(red,green,blue))*100/255)
            red = red * brightness_ratio
            green = green * brightness_ratio
            blue = blue * brightness_ratio            
            self.state.red = math.floor(red)
            self.state.green = math.floor(green)
            self.state.blue = math.floor(blue)
            print(f"sync state: {self.state}")



    async def sync_data(self):
        await self.get_light_data()
        await asyncio.sleep(1)
        await self.get_time_data()


    async def get_light_data(self):
        print('get_light_data')
        if not self.client.is_connected:
            print('Device is not connected. HALT')
            return
        data = bytes([-17 & 0xff, 1, 119]) #get light data
        await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,data)


    async def get_time_data(self):
        print('get_time_data')
        if not self.client.is_connected:
            print('Device is not connected. HALT')
            return
        data = bytes([36, 42, 43, 66]) #get light data
        await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,data)

    async def pair(self)-> bool:
        return await self.client.pair()
    # functions
    async def set_power(self,state:bool):
        if await self.connect():
            onOffCommand = bytes([-52 & 0xff, 35, 51])
            if not state:
                onOffCommand = bytes([-52 & 0xff, 36, 51])
           
            await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,onOffCommand,True)
           
        else:
           raise Exception(f"device {self.address} is not connected")


    async def set_color(self,**color):
        #  byte[] bArr = {86, (byte) ((Color.red(myColor.color) * myColor.progress) / 100), (byte) ((Color.green(myColor.color) * myColor.progress) / 100), (byte) ((Color.blue(myColor.color) * myColor.progress) / 100), (byte) (((myColor.warmWhite * myColor.progress) / 100) & 255), -16, -86};
        #         synTimedata((byte) 65, (byte) ((Color.red(myColor.color) * myColor.progress) / 100), (byte) ((Color.red(myColor.color) * myColor.progress) / 100), (byte) ((Color.green(myColor.color) * myColor.progress) / 100), (byte) ((Color.blue(myColor.color) * myColor.progress) / 100), (byte) 0);
        #         if (myColor.warmWhite != 0) {
        #             bArr[1] = 0;
        #             bArr[2] = 0;
        #             bArr[3] = 0;
        #             bArr[5] = 15;
        #             bArr[4] = (byte) (((myColor.progress * 255) / 100) & 255);
        #             synTimedata((byte) 65, (byte) 0, (byte) 0, (byte) 0, (byte) 0, (byte) (((myColor.progress * 255) / 100) & 255));
        #         }
       
        brightness =color.get('brightness')
        brightness = 3 if brightness<3 else brightness
        red = color.get('red')
        green = color.get('green')
        blue = color.get('blue')
        data = bytes([86,int(red*brightness/100),int(green*brightness/100),int(blue*brightness/100),0, -16 & 0xff, -86 & 0xff])
        await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,data)
        self.state.set_state(red,green,blue,brightness)
