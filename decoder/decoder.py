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
    if 'lht65' in device_id:
        fields = decode_lht65.decode(payload)
    elif device_id.startswith('elsys') or (device_id[:3] in ('ers', 'elt')):
        fields = decode_elsys.decode(payload)
    else:
        # no decoder for this payload
        fields = {}

    # some decoders will give a list of values back for one field.  If requested, convert 
    # these into multiple fields with an underscore index at end of field name.
    if flatten_value_lists:
        for k, v in fields.items():
            if type(v) == list:
                del fields[k]     # remove that item cuz will add individual elements
                for ix, val in enumerate(v):
                    fields[f'{k}_{ix}'] = val

    # Add these fields to the results dictionary
    results['fields'] = fields

    return results
