import asyncio
from logging import getLogRecordFactory
from bleak import BleakClient
import math
from device.my_color import MyColor
from .device_state import DeviceState


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
        self.auto_reconnect = True
        self.is_connecting = False
        self.reconnect_task = None
        
        
    
    def on_disconnected(self, client):
        print(f'device {self.address} is disconnected')
        asyncio.create_task(self.re_connect(3))

    async def re_connect(self, timeout =0):
        await asyncio.sleep(timeout)
        if not self.client.is_connected:            
            try:
                if not self.is_connecting:
                    print(f'Reconnecting to {self.address}')
                    is_connected = await self.connect()   
                    if not is_connected:
                        print(f'Reconnecting FAIL. retry in {timeout}')
                    
                        self.reconnect_task = asyncio.create_task(self.re_connect(timeout=timeout))
                
            except Exception as e:
                print(e) 
            

    async def connect(self) -> bool:        
        if not self.client.is_connected:
            try:
                print(f'connecting to HappyLightDevice at {self.address}')
                if self.is_connecting:
                    raise Exception('Already Reconnecting');
                self.is_connecting = True
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
            except Exception as e:
                print(e)          
            finally:
                self.is_connecting = False
                print(f'is_connected: {self.client.is_connected}, auto_reconnect: {self.auto_reconnect}')
                if not self.client.is_connected and self.auto_reconnect:
                    asyncio.create_task(self.re_connect(3))
                    return False

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
            brightness = math.ceil(float(max(red,green,blue))*100/255)
            red = red * brightness_ratio
            green = green * brightness_ratio
            blue = blue * brightness_ratio            
            self.state.color = MyColor(math.ceil(red),math.ceil(green), math.ceil(blue), brightness)
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
    async def set_power(self,state:bool) -> bool:
        if await self.connect():
            onOffCommand = bytes([-52 & 0xff, 35, 51])
            if not state:
                onOffCommand = bytes([-52 & 0xff, 36, 51])
           
            await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,onOffCommand,True)
            self.state.power_state = state
            return True
           
        else:
           raise Exception(f"device {self.address} is not connected")


    async def set_power_slowly(self, state:bool):
        if state == self.state.power_state:
            return True
        saved_brightness = self.state.color.brightness
        init_brightness = self.state.color.brightness if self.state.power_state else 0
        target_brightness = self.state.color.brightness if init_brightness == 0 else 0
        divied_portion = 50
        step = saved_brightness / divied_portion
        current_brightness = init_brightness
        await self.set_dimmer(math.ceil(current_brightness))
        if state:
            await self.set_power(True)
        print(f'set_power_slowly: {state}, init:{init_brightness}, target:{target_brightness}, saved: {saved_brightness}')
        for x in range(divied_portion):
            
            if(target_brightness>init_brightness):
                current_brightness += step
            else:
                 current_brightness -= step
            # print(f'current:{current_brightness}, target:{target_brightness}')
            await self.set_dimmer(math.ceil(current_brightness))
            await asyncio.sleep(10/1000)
        await self.set_power(state)
        await asyncio.sleep(50/1000)
        await self.set_dimmer(math.ceil(saved_brightness))



    async def set_dimmer(self,brightness:int):
        await self.set_rgb_color(red=self.state.color.red,green=self.state.color.green,blue = self.state.color.blue, brightness=brightness)

    async def set_color(self,color:MyColor)-> bool:
        return await self.set_rgb_color(red=color.red, green=color.green, blue = color.blue, brightness=color.brightness)

    async def set_rgb_color(self,**color)-> bool:
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
        if await self.connect():
            brightness =color.get('brightness')
            brightness = 3 if brightness<3 else brightness
            red = color.get('red')
            green = color.get('green')
            blue = color.get('blue')
            data = bytes([86,int(red*brightness/100),int(green*brightness/100),int(blue*brightness/100),0, -16 & 0xff, -86 & 0xff])
            await self.client.write_gatt_char(HappyLightDevice.CONSMART_BLE_NOTIFICATION_CHARACTERISTICS_WRGB_UUID,data)
            self.state.set_state(MyColor(red,green,blue,brightness))
            return True
        return False
