



##### start URL Builder

import time,base64,hmac,hashlib
import urllib.parse

KEY_ID = '' # input your amazon key id
AWS_SECRET_ACCESS_KEY = b'' #input your Amazon Web Service secret access key

PREPEND = b"""GET
webservices.amazon.com
/onca/xml
"""

BASE_URL = 'http://webservices.amazon.com/onca/xml?'




def urlBuild(optionalParameters):
    fixedParameters = {'Service':'AWSECommerceService',
                       'Version':'2009-03-31',
                       'AWSAccessKeyId':KEY_ID,
                       'Timestamp':time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
    if 'Power' in optionalParameters:
        optionalParameters['Power'] = optionalParameters['Power'].replace(' ','+')
    allParameters = dict(optionalParameters)
    allParameters.update(fixedParameters)
    keys = allParameters.keys()
    keys = list(keys)
    keys.sort()
    values = map(allParameters.get, keys)
    url_string = urllib.parse.urlencode(list(zip(keys,values)))
    stringToSign = (PREPEND + url_string.encode())
    signature = signatureBuilder(AWS_SECRET_ACCESS_KEY, stringToSign)
    signedUrl = BASE_URL + url_string + signature
    return signedUrl

def signatureBuilder(key,toSign):
    #Pre: takes key (AWS secret code) and toSign as bite strings
    #Post: returns regular string amazon 'signature'
    signature = (base64.b64encode(hmac.new(key, msg=toSign, digestmod=hashlib.sha256).digest()))
    return '&Signature='+signReplace(signature.decode())#signat

def signReplace(urlIn):##can prob replace w/encode function
    newUrl = ''
    for letter in urlIn:
        if letter == '+':
            newUrl += '%2B'
        elif letter == '=':
            newUrl += '%3D'
        else:
            newUrl += letter
    return newUrl

##### End Url Builder

##### Start Letter Generator

def threeLetterGenerator():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                yield a+b+c

##### Start Letter Generator
