import sys, os, base64, datetime, hashlib, hmac
import json
import requests
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    # AWS Version 4 signing
    # Translate API (TranslateText)

    # Python can read the AWS access key from environment variables or the configuration file. 
    # In this example, keys are stored in environment variables. As a best practice, do not 
    # embed credentials in code.
    if 'AWS_ACCESS_KEY_ID' not in app.config or \
            not app.config['AWS_ACCESS_KEY_ID'] or \
            'AWS_SECRET_ACCESS_KEY' not in app.config or \
            not app.config['AWS_SECRET_ACCESS_KEY']:
        return _('Error: the translation service is not configured.')

    # ************* REQUEST VALUES *************
    method = 'POST'
    service = 'translate'
    region = app.config['AWS_DEFAULT_REGION']
    host = service + '.' + region + '.amazonaws.com'
    endpoint = 'https://' + host + '/'
    content_type = 'application/x-amz-json-1.1'
    amz_target = 'AWSShineFrontendService_20170701.TranslateText'
    request_parameters =  '{'
    request_parameters +=  '"Text": "{}",'.format(text)
    request_parameters +=  '"SourceLanguageCode": "{}",'.format(source_language)
    request_parameters +=  '"TargetLanguageCode": "{}"'.format(dest_language)
    request_parameters +=  '}'

    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def getSignatureKey(key, date_stamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d') # The date without time is used in the credential scope.

    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    canonical_uri = '/'
    canonical_querystring = ''
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' + 'x-amz-target:' + amz_target + '\n'
    signed_headers = 'content-type;host;x-amz-date;x-amz-target'
    payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    signing_key = getSignatureKey(app.config['AWS_SECRET_ACCESS_KEY'], date_stamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    authorization_header = algorithm + ' ' + 'Credential=' + app.config['AWS_ACCESS_KEY_ID'] + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    headers = {'Content-Type':content_type,
           'X-Amz-Date':amz_date,
           'X-Amz-Target':amz_target,
           'Authorization':authorization_header}

    # ************* TASK 5: SEND THE REQUEST *************
    r = requests.post(endpoint, data=request_parameters, headers=headers)

    if r.status_code != 200:
        return _('Error: the translation service failed.')
    r_dict = json.loads(r.content.decode('utf-8-sig'))
    return r_dict.get('TranslatedText')
