# hack to show connection to backend server
# will sign message correctly and POST sound data
# you will need to modify this to send WAV data and record data with the ESP32
# this is micropython code v 1.20
#
import binascii  # base64
import hashlib
import hmac
import os
import sys
import time
import urequests
import network
import utime

def make_request(data, blob_data=None):
    boundary = binascii.hexlify(uos.urandom(16)).decode('ascii')

    def encode_field(field_name):
        return (
            b'--%s' % boundary,
            b'Content-Disposition: form-data; name="%s"' % field_name,
            b'',
            b'%s' % data[field_name]
        )

    def encode_file(field_name):
        fn = 'sample.mp3'
        return (
            b'--%s' % boundary,
            b'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename),
            b'Content-Type: application/octetstream'
            b'',
            b'',
            blob_data
        )

    lines = []
    for name in data:
        lines.extend(encode_field(name))

    if blob_data:
        lines.extend(encode_file('sample'))

    lines.extend((b'--%s--' % boundary, b''))

    body = b'\r\n'.join(lines)

    headers = {"Accept-Charset": "utf-8",
               'Content-Type': 'multipart/form-data; boundary=' + boundary}

    return body, headers

# work starts here


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('OETELX', '12345XXXXX')
    while not wlan.isconnected():
        print('no metwork yet')
        utime.sleep_ms(300)        
        pass

# we have network now, we can call the internet


access_key = "a6b1777ce3a7900ebc830eae91bf7XXX" # add your access key, this is not valid
access_secret = "2mtC9ACj1P7AdxfVQ6bEUeW63p4urUuwFQRKvXXX" # add your access_secret, this is not valid
requrl = "http://identify-eu-west-1.acrcloud.com/v1/identify"
http_method = "POST"
http_uri = "/v1/identify"

# default is "fingerprint", it's for recognizing fingerprint, 
# if you want to identify audio, please change data_type="audio"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
    timestamp)

sign = binascii.b2a_base64(
    hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'), digestmod=hashlib.sha1).digest()).decode(
    'ascii')
sign = sign[:-1]  # strip newline Edwin was here bugfixing 24-4-2023


# suported file formats: mp3,wav,wma,amr,ogg, ape,acc,spx,m4a,mp4,FLAC, etc
# File size: < 1M , You'de better cut large file to small file, within 15 seconds data size is better
filename = 'test.mp3'
x = os.stat(filename)

sample_bytes = x[6] # get file size from tuple

data = {'access_key': access_key,
        'sample_bytes': sample_bytes,
        'timestamp': str(timestamp),
        'signature': sign,
        'data_type': data_type,
        "signature_version": signature_version}

blob_file = open(filename, 'rb')
blob = blob_file.read()
blob_file.close()
b, h = make_request(data=data, blob_data=blob)


r = urequests.request('POST', requrl, headers=h, data=b)
r.encoding = "utf-8"
print(r.text)
