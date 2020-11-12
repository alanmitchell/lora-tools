"""Module that decodes a LoRaWAN HTTP Integration payload into a field/value
dictionary.
"""
from typing import Dict, Any
import base64

from dateutil.parser import parse

from . import decode_elsys
from . import decode_lht65

def decode(
    integration_payload: Dict[str, Any],
    flatten_value_lists=True,
    ) -> Dict[str, float]:
    """ Returns a dictionary of information derived from the payload sent by 
    a Things Network HTTP Integration.  Some general data about the message is included
    (e.g. Unix timestamp) but a full list of the sensor values encoded in the payload are returned
    in the 'fields' key of the dictionary. Sensor values from the following sensors can currently be
    decoded:
        All Elsys sensors
        Drgaino LHT65 sensors
    
    Function Parameters are:
    'integration_payload': the data payload that is sent by a Things Network HTTP integration, 
        in Python dictionary format.
    'flatten_value_lists': some sensors, including the Elsys ELT-2, decode multiple sensor channels 
        into a list of values, for example multiple external temperature channels.  If this parameter
        is True (the default), those lists are flattened into separate sensor values by appending
        the list index to the sensor name.
    """

    # Go here to learn about the format of an HTTP Integration Uplink coming from the Things
    # network:  https://www.thethingsnetwork.org/docs/applications/http/
    device_id = integration_payload['dev_id']
    device_eui = integration_payload['hardware_serial']
    payload = base64.b64decode(integration_payload['payload_raw'])  # is a list of bytes now

    # Make UNIX timestamp for the record
    ts = parse(integration_payload['metadata']['time']).timestamp()

    # Extract the strongest SNR across the gateways that received the transmission.  And record
    # the RSSI from that gateway.
    sigs = [(gtw['snr'], gtw['rssi']) for gtw in integration_payload['metadata']['gateways']]
    snr, rssi = max(sigs)

    # the dictionary that will hold the decoded results
    results = {
        'device_id': device_id,
        'device_eui': device_eui,
        'ts': ts,
        'data_rate': integration_payload['metadata']['data_rate'],
        'snr': snr,           # SNR from best gateway
        'rssi': rssi,         # RSSI from the gateway with the best SNR
        'gateway_count': len(integration_payload['metadata']['gateways']),
    }

    # dispatch to the right decoding function based on characters in the device_id.
    # if device_id contains "lht65" anywhere in it, use the lht65 decoder
    # if device_id starts with "ers" or "elsys" or "elt", use the elsys decoder
    dev_id_lwr = device_id.lower()    # get variable for lower case device ID
    if 'lht65' in dev_id_lwr:
        fields = decode_lht65.decode(payload)
    elif dev_id_lwr.startswith('elsys') or (dev_id_lwr[:3] in ('ers', 'elt')):
        fields = decode_elsys.decode(payload)
    else:
        # no decoder for this payload
        fields = {}

    # some decoders will give a list of values back for one field.  If requested, convert 
    # these into multiple fields with an underscore index at end of field name.
    if flatten_value_lists:
        flat_fields ={}
        fields_to_delete = []
        for k, v in fields.items():
            if type(v) == list:
                fields_to_delete.append(k)
                for ix, val in enumerate(v):
                    flat_fields[f'{k}_{ix}'] = val
        for k in fields_to_delete:
            del fields[k]     # remove that item cuz will add individual elements
        fields.update(flat_fields)

    # Add these fields to the results dictionary
    results['fields'] = fields

    return results

def test():
    from pprint import pprint
    recs = [
        {"app_id":"an-dragino","dev_id":"lht65-a84041000181c74e","hardware_serial":"A84041000181C74E","port":2,"counter":33041,"payload_raw":"yxH5YAKWAfl8f/8=","payload_fields":{"bat_v":2.833,"humidity":"66.2","temp_ext":"1.98","temp_int":"1.47"},"metadata":{"time":"2020-10-30T02:35:43.883078268Z","frequency":904.7,"modulation":"LORA","data_rate":"SF7BW125","coding_rate":"4/5","gateways":[{"gtw_id":"eui-a84041ffff1ee2b4","timestamp":3580480955,"time":"2020-10-30T02:35:43.828704Z","channel":4,"rssi":-90,"snr":8,"rf_chain":0}]},"downlink_url":"https://integrations.thethingsnetwork.org/ttn-us-west/api/v2/down/an-dragino/lora-signal?key=ttn-account-v2.vL5tZaRYIpvsQiQb8Iy48z6u0hqi3BIIaCS8yubFMgU"},
        {"app_id":"sig-strength","dev_id":"elt-a81758fffe0523db","hardware_serial":"A81758FFFE0523DB","port":5,"counter":167,"payload_raw":"Bw4uDQE=","metadata":{"time":"2020-11-08T18:50:21.145287118Z","frequency":904.7,"modulation":"LORA","data_rate":"SF9BW125","coding_rate":"4/5","gateways":[{"gtw_id":"eui-58a0cbfffe8015fd","timestamp":1861174284,"time":"2020-11-08T18:50:21.086786985Z","channel":0,"rssi":-51,"snr":9.25,"rf_chain":0},{"gtw_id":"eui-a84041ffff1ee2b4","timestamp":471103348,"time":"2020-11-08T18:50:21.099979Z","channel":4,"rssi":-53,"snr":11,"rf_chain":0}]},"downlink_url":"https://integrations.thethingsnetwork.org/ttn-us-west/api/v2/down/sig-strength/lora-signal?key=ttn-account-v2.sgTyWsa1SlDoilFxQU6Q7TAWL80RhMYrM1dajv7Ej8k"},    
        {"app_id":"sig-strength","dev_id":"elt-a81758fffe0523db","hardware_serial":"A81758FFFE0523DB","port":5,"counter":167,"payload_raw":"AQDiAikEACcFBgYDCAcNYhkAARn//w==","metadata":{"time":"2020-11-08T18:50:21.145287118Z","frequency":904.7,"modulation":"LORA","data_rate":"SF9BW125","coding_rate":"4/5","gateways":[{"gtw_id":"eui-58a0cbfffe8015fd","timestamp":1861174284,"time":"2020-11-08T18:50:21.086786985Z","channel":0,"rssi":-51,"snr":9.25,"rf_chain":0},{"gtw_id":"eui-a84041ffff1ee2b4","timestamp":471103348,"time":"2020-11-08T18:50:21.099979Z","channel":4,"rssi":-53,"snr":11,"rf_chain":0}]},"downlink_url":"https://integrations.thethingsnetwork.org/ttn-us-west/api/v2/down/sig-strength/lora-signal?key=ttn-account-v2.sgTyWsa1SlDoilFxQU6Q7TAWL80RhMYrM1dajv7Ej8k"},    
    ]
    for rec in recs:
        pprint(decode(rec))

    pprint(decode(recs[-1], flatten_value_lists=False))

if __name__ == '__main__':
    # To run this without import error, need to run "python -m decoder.decoder" from the top level directory.
    test()
