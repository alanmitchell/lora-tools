"""Module that decodes a LoRaWAN HTTP Integration payload into a field/value
dictionary.
"""
from typing import Dict, Any
import base64

def decode(integration_payload: Dict[str, Any]) -> Dict[str, float]:
    """Returns a dictionary of engineering values, keyed on field name that
    is decoded from 'integration_payload'.  'integration_payload' is the data
    payload that is sent by a Things Network HTTP integration, in Python dictionary
    format.
    """

    # the dictionary that will hold the decoded results
    results = {}

    # Go here to learn about the format of an HTTP Integration Uplink coming from the Things
    # network:  https://www.thethingsnetwork.org/docs/applications/http/
    device_id = integration_payload['dev_id']
    device_eui = integration_payload['hardware_serial']
    payload = base64.b64decode(integration_payload['payload_raw'])  # is a list of bytes now

    # extract out the SNR and RSSI and put them in the results dictionary, just as was done
    # here:
    # https://github.com/alanmitchell/bmon/blob/4a2509c497f4364c17c9257e30cf0976569b5ebb/bmsapp/views.py#L297

    # dispatch to the right decoding function based on characters in the device_id.
    # if device_id contains "lht65" anywhere in it, use the lht65 decoder
    # if device_id starts with "ers" or "elsys" or "elt", use the elsys decoder

    # Use the dictionry update function to add in the results from the decoder into the
    # dictionary you started above.

    # All of the field keys returned start with the "[device EUI]_"
    # Use Python F-strings to create these keys.

    # For the lht65 and Elsys decoder functions, convert Temperature values to degrees F
    # instead of the degrees C that comes out of the Javascript version of the functions.

    return results

def decode_lht65(payload: bytes) -> Dict[str, float]:
    """Decoder function for LHT65 sensor.
    Go here for the Javascript decoder:  http://www.dragino.com/downloads/downloads/LHT65/payload_decode/ttn_payload_decode.txt
    Here for the User Manual:  http://www.dragino.com/downloads/index.php?dir=LHT65/UserManual/
    """
    pass

def decode_elsys(payload: bytes) -> Dict[str, float]:
    """Decoder function for Elsys sensors.
    Go here to find the Javascript version of a decoder, and to find an online calculator
    that implements the decoding:  https://www.elsys.se/en/elsys-payload/
    """
    pass
