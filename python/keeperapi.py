import sys
import json
import requests
import base64
import getpass
import time
from keepererror import AuthenticationError
from keepererror import CommunicationError
from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto import Random

CLIENT_VERSION = 'c9.0.0'
current_milli_time = lambda: int(round(time.time() * 1000))

def login(params):
    """Login to the server and get session token"""
    
    if not params.salt:
        payload = {'command':'account_summary',
                   'include':['license','settings','group','keys'],
                   'client_version':CLIENT_VERSION,
                   'username':params.email}

        try:
            r = requests.post(params.server, json=payload)
        except:
            raise CommunicationError(sys.exc_info()[0])

        if params.debug:
            print('')
            print('>>> Request server:[' + params.server + ']')
            print('>>> Request JSON:[' + str(payload) + ']')
            print('')
            print('<<< Response Code:[' + str(r.status_code) + ']')
            print('<<< Response Headers:[' + str(r.headers) + ']')
            print('<<< Response content:[' + str(r.text) + ']')

        if not 'salt' in r.json():
            if r.json()['result_code'] == 'auth_failed':
                raise AuthenticationError('Pre-auth failed.')

        # server doesn't include == at the end, but the module expects it
        params.salt = base64.urlsafe_b64decode(r.json()['salt']+'==')
        params.iterations = r.json()['iterations']
    
        prf = lambda p,s: HMAC.new(p,s,SHA256).digest()
        tmp_auth_verifier = base64.urlsafe_b64encode(
            PBKDF2(params.password, params.salt, 
                32, params.iterations, prf))

        # converts b'xxxx' to xxxx
        params.auth_verifier = tmp_auth_verifier.decode()

        if params.debug:
            print('<<< Auth Verifier:['+str(params.auth_verifier)+']')


    success = False
    while not success:

        if params.mfa_token:
            payload = {
                   'command':'login', 
                   'include':['keys'],
                   'version':2, 
                   'auth_response':params.auth_verifier,
                   'client_version':CLIENT_VERSION,
                   '2fa_token':params.mfa_token,
                   '2fa_type':params.mfa_type, 
                   'username':params.email
                  }

        else:
            payload = {
                   'command':'login', 
                   'version':2, 
                   'auth_response':params.auth_verifier,
                   'client_version':CLIENT_VERSION,
                   'username':params.email
                  }

        try:
            r = requests.post(params.server, json=payload)
        except:
            raise CommunicationError(sys.exc_info()[0])

        response_json = r.json()

        if params.debug:
            print('')
            print('>>> Request server:[' + params.server + ']')
            print('>>> Request JSON:[' + str(payload) + ']')
            print('')
            print('<<< Response Code:[' + str(r.status_code) + ']')
            print('<<< Response Headers:[' + str(r.headers) + ']')
            print('<<< Response content:[' + json.dumps(response_json, 
                sort_keys=True, indent=4) + ']')
            print('<<< Session Token:['+str(params.session_token)+']')

        if (
            response_json['result_code'] == 'auth_success' and 
            response_json['result'] == 'success'
            ):
            if params.debug: print('Auth Success')

            if 'session_token' in response_json:
                params.session_token = response_json['session_token']

            if 'device_token' in response_json:
                params.mfa_token = response_json['device_token']
                print('----> Device token: ' + str(params.mfa_token))

            if params.mfa_token:
                params.mfa_type = 'device_token'

            if 'keys' in response_json:
                params.encrypted_private_key = \
                    response_json['keys']['encrypted_private_key']
                params.encryption_params = \
                    response_json['keys']['encryption_params']

                decrypt_data_key(params)
                decrypt_private_key(params)


            success = True

        elif ( response_json['result_code'] == 'need_totp' or
               response_json['result_code'] == 'invalid_device_token' or
               response_json['result_code'] == 'invalid_totp'):
            try:
                params.mfa_token = '' 
                params.mfa_type = 'one_time'

                while not params.mfa_token:
                    params.mfa_token = getpass.getpass(
                        prompt='2FA Code: ', stream=None)

            except (KeyboardInterrupt, SystemExit):
                return 
                
        elif response_json['result_code'] == 'auth_failed':
            raise AuthenticationError(response_json['result_code'])

        elif response_json['result_code'] == 'throttled':
            raise AuthenticationError(response_json['message'])

        elif response_json['result_code']:
            raise AuthenticationError(response_json['result_code'])

        else:
            raise CommunicationError('Unknown problem')

def sync_down(params):
    if not params.session_token:
        try:
            login(params)
        except:
            raise
            
    payload = {
               'include':[
                   'sfheaders',
                   'sfrecords',
                   'sfusers',
                   'sfteams'
               ],
               'revision':params.revision,
               'client_time':current_milli_time(),
               'device_id':'Commander', 
               'device_name':'Commander', 
               'command':'sync_down', 
               'protocol_version':1, 
               'client_version':CLIENT_VERSION,
               '2fa_token':params.mfa_token,
               '2fa_type':params.mfa_type, 
               'session_token':params.session_token, 
               'username':params.email
              }

    try:
        r = requests.post(params.server, json=payload)
    except:
        raise CommunicationError(sys.exc_info()[0])

    response_json = r.json()

    if params.debug:
        print('')
        print('>>> Request server:[' + params.server + ']')
        print('>>> Request JSON:[' + str(payload) + ']')
        print('')
        print('<<< Response Code:[' + str(r.status_code) + ']')
        print('<<< Response Headers:[' + str(r.headers) + ']')
        print('<<< Response content:[' + json.dumps(response_json, 
            sort_keys=True, indent=4) + ']')

    if response_json['result'] == 'success':

        if 'full_sync' in response_json:
            if response_json['full_sync']:
                if params.debug: print('Full Sync response')
                params.record_cache = {}  
                params.meta_data_cache = {}  
                params.shared_folder_cache = {}  

        if 'revision' in response_json:
            params.revision = response_json['revision']
    
        # TBD partial sync stuff doesnt work yet
        #if 'removed_records' in response_json:
        #    for uid in response_json['removed_records']:
        #        for record in record_cache:
        #            if record['record_uid'] == uid 
        #                params.record_cache.remove(record)
    
        # TBD partial sync stuff doesnt work
        #if 'removed_shared_folders' in response_json:
        #    for uid in response_json['removed_shared_folders']:
        #        for shared_folder in shared_folder_cache:
        #            if shared_folder['shared_folder_uid'] == uid 
        #                params.shared_folder_cache.remove(shared_folder)
        
        if 'record_meta_data' in response_json:
            for meta_data in response_json['record_meta_data']:
                print('meta_data: ' + str(meta_data)) 
                params.meta_data_cache[meta_data['record_uid']] = meta_data
    
        if 'records' in response_json:
            for record in response_json['records']:
                params.record_cache[record['record_uid']] = record

        if 'shared_folders' in response_json:
            for shared_folder in response_json['shared_folders']:
                params.shared_folder_cache[shared_folder['shared_folder_uid']] = shared_folder

        if 'pending_shares_from' in response_json:
            print('FYI: You have pending share requests.')

        if params.debug:
            print('--- Meta Data Cache: ' + str(params.meta_data_cache))
            print('--- Record Cache: ' + str(params.record_cache))
            print('--- Folders Cache: ' + str(params.shared_folder_cache))

        # Decrypt the data!

    else :
        raise CommunicationError('Unknown problem')

def decrypt_data_key(params):
    """ Decrypt the data key returned by the server 
    Format:
    1 byte: Version number (currently only 1)
    3 bytes: Iterations, unsigned integer, big endian
    16 bytes: salt
    80 bytes: encrypted data key (broken down further below)
    16 bytes: IV
    64 bytes: ciphertextIn
    Key for encrypting the data key: 
        PBKDF2_with_HMAC_SHA256(iterations, salt, master password, 256-bit)
    Encryption method: 256-bit AES, CBC mode, no padding
    Verification: the decrypted ciphertext should contain two 32 byte values, 
        identical to each other.
    """

    decoded_encryption_params = base64.urlsafe_b64decode(
        params.encryption_params+'==')

    if len(decoded_encryption_params) != 100:
        raise CryptoError('Invalid encryption params: bad params length')

    version = int.from_bytes(decoded_encryption_params[0:1], 
                              byteorder='big', signed=False)
    iterations = int.from_bytes(decoded_encryption_params[1:4], 
                                 byteorder='big', signed=False)
    salt = decoded_encryption_params[4:20]
    encrypted_data_key = decoded_encryption_params[20:100]
    iv = encrypted_data_key[0:16]
    ciphertext = encrypted_data_key[16:80]

    if iterations < 1000:
        raise CryptoError('Invalid encryption parameters: iterations too low')

    # generate cipher key from master password and encryption params
    prf = lambda p,s: HMAC.new(p,s,SHA256).digest()
    key = PBKDF2(params.password, salt, 32, iterations, prf)

    # decrypt the <encrypted data key>
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data_key = cipher.decrypt(ciphertext)

    # validate the key is formatted correctly
    if len(decrypted_data_key) != 64:
        raise CryptoError('Invalid data key length')

    if decrypted_data_key[0:32] != decrypted_data_key[32:64]:
        raise CryptoError('Invalid data key: failed mirror verification')

    if params.debug: print('Decrypted data key with success.')

    # save the encryption params 
    params.data_key = decrypted_data_key[0:32] 


def decrypt_private_key(params):
    """ Decrypt the RSA private key
    PKCS1 formatted private key, which is described by the ASN.1 type:
    RSAPrivateKey ::= SEQUENCE {
          version           Version,
          modulus           INTEGER,  -- n
          publicExponent    INTEGER,  -- e
          privateExponent   INTEGER,  -- d
          prime1            INTEGER,  -- p
          prime2            INTEGER,  -- q
          exponent1         INTEGER,  -- d mod (p-1)
          exponent2         INTEGER,  -- d mod (q-1)
          coefficient       INTEGER,  -- (inverse of q) mod p
          otherPrimeInfos   OtherPrimeInfos OPTIONAL
    }
    """
    decoded_private_key = base64.urlsafe_b64decode(
        params.encrypted_private_key+'==')

    if params.debug: print('decoded private key: ' + str(decoded_private_key))

    iv = decoded_private_key[0:16]
    ciphertext = decoded_private_key[16:len(decoded_private_key)]

    print('decrypted data key: ' + str(params.data_key))

    cipher = AES.new(params.data_key, AES.MODE_CBC, iv)
    decrypted_private_key = cipher.decrypt(ciphertext)
    
    if params.debug: 
        print('decrypted private key: ' + str(decrypted_private_key))
    

def display_folders_titles_uids(json_to_show):
    pass
