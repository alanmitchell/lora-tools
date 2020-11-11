"""Module for decoding the Payload from Elsys LoRaWAN sensors.
See Javascript Elsys decoder at:  https://www.elsys.se/en/elsys-payload/
"""
from typing import Dict, Any

def bin16dec(bin: int) -> int:
    """Returns twos complement value from a 16-bit integer
    """
    num = (bin & 0xFFFF)
    return -(0x010000 - num) if (0x8000 & num) else num

def bin8dec(bin: int) -> int:
    """Return twos complement value from an 8-bit integer
    """
    num = bin & 0xFF
    return -(0x0100 - num) if (0x80 & num) else num

def decode(data: bytes) -> Dict[str, float]:
    """Returns a dictionary of enginerring values decoded from an Elsys Uplink Payload.
    The payload 'data' is a byte array.
    Works with all Elsys LoRaWAN sensors.
    Converts temperatures to Fahrenheit instead of Celsius like the original Elsys decoder.
    """

    # holds the dictionary of results
    res = {}

    def int16(ix):
        """Returns a 16-bit integer from the 2 bytes starting at index 'ix' in data byte array.
        """
        return (data[ix] << 8) | (data[ix + 1])

    def temp(i):
        # converts to Fahrenheit.
        temp = int16(i+1)
        temp = bin16dec(temp) / 10
        res['temperature'] = temp * 1.8 + 32.0
        return 2

    def rh(i):
        res['humidity'] = data[i + 1]
        return 1

    def acc(i):
        res['x'] = bin8dec(data[i + 1])
        res['y'] = bin8dec(data[i + 2])
        res['z'] = bin8dec(data[i + 3])
        return 3

    def light(i):
        res['light'] = int16(i+1)
        return 2

    def motion(i):
        res['motion'] = (data[i + 1])
        return 1

    def co2(i):
        res['co2'] = int16(i+1)
        return 2

    def vdd(i):
        res['vdd'] = int16(i+1)
        return 2

    def analog1(i):
        res['analog1'] = int16(i+1)
        return 2

    def gps(i):
        res['lat'] = (data[i + 1] | data[i + 2] << 8 | data[i + 3] << 16 | (0xFF << 24 if data[i + 3] & 0x80 else 0)) / 10000
        res['long'] = (data[i + 4] | data[i + 5] << 8 | data[i + 6] << 16 | (0xFF << 24 if data[i + 6] & 0x80 else 0)) / 10000
        return 6

    def pulse1(i):
        res['pulse1'] = int16(i+1)
        return 2

    def pulse1_abs(i):
        res['pulseAbs'] = (data[i + 1] << 24) | (data[i + 2] << 16) | (data[i + 3] << 8) | (data[i + 4])
        return 4

    def ext_temp1(i):
        temp = int16(i+1)
        temp = bin16dec(temp) / 10
        res['externalTemperature'] = temp * 1.8 + 32.0
        return 2

    def ext_digital(i):
        res['digital'] = data[i + 1]
        return 1

    def ext_distance(i):
        res['distance'] = int16(i+1)
        return 2

    def acc_motion(i):
        res['accMotion'] = data[i + 1]
        return 1

    def ir_temp(i):
        iTemp = int16(i+1)
        iTemp = bin16dec(iTemp)
        eTemp = int16(i + 3)
        eTemp = bin16dec(eTemp)
        res['irInternalTemperature'] = iTemp / 10 * 1.8 + 32.0
        res['irExternalTemperature'] = eTemp / 10 * 1.8 + 32.0
        return 4

    def occupancy(i):
        res['occupancy'] = data[i + 1]
        return 1

    def waterleak(i):
        res['waterleak'] = data[i + 1]
        return 1

    def grideye(i):
        ref = data[i+1]
        res['grideye'] = [ref + data[i + 2 + j] / 10.0 for j in range(64)]
        return 64

    def pressure(i):
        press = (data[i + 1] << 24) | (data[i + 2] << 16) | (data[i + 3] << 8) | (data[i + 4])
        res['pressure'] = press / 1000
        return 4

    def sound(i):
        res['soundPeak'] = data[i + 1]
        res['soundAvg'] = data[i + 2]
        return 2

    def pulse2(i):
        res['pulse2'] = int16(i+1)
        return 2

    def pulse2_abs(i):
        res['pulseAbs2'] = (data[i + 1] << 24) | (data[i + 2] << 16) | (data[i + 3] << 8) | (data[i + 4])
        return 4

    def analog2(i):
        res['analog2'] = int16(i+1)
        return 2

    def ext_temp2(i):
        temp = int16(i+1)
        temp = bin16dec(temp) / 10 * 1.8 + 32.0
        try:
            exist_rd =  res['externalTemperature2']
            # there already is a Temperature 2 reading, 
            if type(exist_rd) == list:
                # the existing value is already a list of readings.  Append to it.
                res['externalTemperature2'].append(temp)
            else:
                # one existing reading. make a list.
                res['externalTemperature2'] = [exist_rd, temp]
        except:
            # this is the first External Temperature 2 reading.
            res['externalTemperature2'] = temp
        
        return 2

    def ext_digital2(i):
        res['digital2'] = data[i + 1]
        return 1

    def ext_analog_uv(i):
        res['analogUv'] = (data[i + 1] << 24) | (data[i + 2] << 16) | (data[i + 3] << 8) | (data[i + 4])
        return 4

    # list of deconding functions, in their type indicator order.
    decode_funcs = [temp, rh, acc, light, motion, co2,
        vdd, analog1, gps, pulse1, pulse1_abs, ext_temp1,
        ext_digital, ext_distance, acc_motion, ir_temp,
        occupancy, waterleak, grideye, pressure, sound,
        pulse2, pulse2_abs, analog2, ext_temp2, ext_digital2,
        ext_analog_uv]

    # make a dictionary that maps a sensor data type code to a decoding function
    decode_func_map = dict(zip(range(1, len(decode_funcs) + 1), decode_funcs))

    # index into payload byte array
    i = 0
    while i < len(data):
        # retrieve the correct decoding function for a sensor of this type
        cur_decode_func = decode_func_map[data[i]]
        # the decoder function adds decoded values to the results dictionary, and it
        # returns the number of bytes consumed by the decoded value.  Add 1 to account for the
        # byte consumed the sensor type identifier.
        i += cur_decode_func(i) + 1

    return res
