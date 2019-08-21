from lib_api_client.client import PaymentClient
from lib_api_client.utils import send_third_party_request
from lib_api_client.session_pool import SessionPool
from requests.auth import HTTPBasicAuth
import uuid


class MPGSClient(PaymentClient):

    def __init__(self, merchant_id, api_password, channel_name='MPGS', timeout=20):
        super(MPGSClient, self).__init__(channel_name, timeout)
        self.session_pool = SessionPool(
            third_party_urls = ['https://ap-gateway.mastercard.com']
        )
        self.merchant_id = merchant_id
        self.auth = HTTPBasicAuth('merchant.{}'.format(merchant_id), api_password)

    def _request(self, path, method, data):
        return send_third_party_request(
            path,
            data,
            method=method,
            channel_name=self.channel_name,
            is_request_json=True,
            auth=self.auth,
            request_session=self.session_pool,
        )


    ##############################
    #
    # 3DS APIs
    #
    ##############################
    def check_3ds_enrollment(self, _3ds_secure_id, callback, session_id):
        _3ds_secure_id = str(uuid.uuid4())
        callback = 'http://eac618e5.ngrok.io'
        path = '/api/rest/version/52/merchant/{}/3DSecureId/{}'.format(self.merchant_id, _3ds_secure_id)
        session_id = ''
        data = {
            'apiOperation': 'CHECK_3DS_ENROLLMENT',
            '3DSecure': {
                'authenticationRedirect': {
                    'responseUrl': callback
                },
            },
            'order': {
                'amount': 100,
                'currency': 'SGD',
            },
            'session': {
                'id': session_id,
            }
        }
        return self._request(path, 'PUT', data)

    def process_acs_result(self):
        pass

    def retrive_3ds_result(self):
        pass

    ##############################
    #
    # Session APIs
    #
    ##############################

    def create_session(self):
        pass

    def retrive_session(self):
        pass

    def update_session(self):
        pass

    ##############################
    #
    # Tokenization APIs
    #
    ##############################

    def create_or_update_token(self):
        pass

    def delete_token(self):
        pass

    def retrive_token(self):
        pass

    def search_tokens(self):
        pass

    ##############################
    #
    # Transaction APIs
    #
    ##############################

    def authorize(self):
        pass

    def inquiry_balance(self):
        pass

    def capture(self):
        pass

    def pay(self):
        pass

    def referral(self):
        pass

    def refund(self):
        pass

    def retrive_order(self):
        pass

    def retrive_transaction(self):
        pass

    def update_authorization(self):
        pass

    def verify(self):
        pass

    def void(self):
        pass
