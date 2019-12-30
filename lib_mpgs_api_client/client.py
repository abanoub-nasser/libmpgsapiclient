from .const import host

from lib_api_client.client import PaymentClient
from lib_api_client.utils import send_third_party_request
from lib_api_client.session_pool import SessionPool

from urlparse import urljoin
from requests.auth import HTTPBasicAuth
import uuid
import json
version = 53


class MPGSClient(PaymentClient):

    def __init__(self, merchant_id, api_password, channel_name='MPGS', timeout=20):
        super(MPGSClient, self).__init__(channel_name, timeout)
        self.session_pool = SessionPool(
            third_party_urls=[host]
        )
        self.merchant_id = merchant_id
        self.auth = HTTPBasicAuth('merchant.{}'.format(merchant_id), api_password)

    def _request(self, path, method, data):
        endpoint = urljoin(host, path)
        return send_third_party_request(
            endpoint,
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
    def check_3ds_enrollment(self, _3ds_secure_id, callback, session_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/3DSecureId/{}'.format(version, self.merchant_id, _3ds_secure_id)
        method = 'PUT'
        data = {
            'apiOperation': 'CHECK_3DS_ENROLLMENT',
            '3DSecure': {
                'authenticationRedirect': {
                    'responseUrl': callback,
                    'pageGenerationMode': 'CUSTOMIZED',
                },
            },
            'order': {
                'amount': amount,
                'currency': currency,
            },
            'session': {
                'id': session_id,
            }
        }
        return self._request(path, method, data)

    def check_3ds_enrollment_with_token(self, token, _3ds_secure_id, callback, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/3DSecureId/{}'.format(version, self.merchant_id, _3ds_secure_id)
        method = 'PUT'
        data = {
            'apiOperation': 'CHECK_3DS_ENROLLMENT',
            '3DSecure': {
                'authenticationRedirect': {
                    'responseUrl': callback,
                    'pageGenerationMode': 'CUSTOMIZED',
                },
            },
            'order': {
                'amount': amount,
                'currency': currency,
            },
            'sourceOfFunds': {
                'token': token,
            },
        }
        return self._request(path, method, data)

    def process_acs_result(self, _3ds_secure_id, payment_authentication_response):
        path = 'api/rest/version/{}/merchant/{}/3DSecureId/{}'.format(version, self.merchant_id, _3ds_secure_id)
        method = 'POST'
        data = {
            'apiOperation': 'PROCESS_ACS_RESULT',
            '3DSecure': {
                'paRes': payment_authentication_response
            },
        }
        return self._request(path, method, data)

    def retrive_3ds_result(self, _3ds_secure_id):
        path = 'api/rest/version/{}/merchant/{}/3DSecureId/{}'.format(version, self.merchant_id, _3ds_secure_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    ##############################
    #
    # Session APIs
    #
    ##############################

    def create_session(self):
        path = 'api/rest/version/{}/merchant/{}/session'.format(version, self.merchant_id)
        method = 'POST'
        data = {}
        return self._request(path, method, data)

    def retrive_session(self, session_id):
        path = 'api/rest/version/{}/merchant/{}/session/{}'.format(version, self.merchant_id, session_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def update_session(self, session_id, card_number, expiry_month, expiry_year, security_code, name):
        path = 'api/rest/version/{}/merchant/{}/session/{}'.format(version, self.merchant_id, session_id)
        method = 'PUT'
        data = {
            'sourceOfFunds': {
                'type': 'CARD',
                'provided': {
                    'card': {
                        'nameOnCard': name,
                        'number': card_number,
                        'securityCode': security_code,
                        'expiry': {
                            'month': expiry_month,
                            'year': expiry_year,
                        }
                    }
                }
            }
        }
        return self._request(path, method, data)

    def update_session_without_cvv(self, session_id, card_number, expiry_month, expiry_year):
        path = 'api/rest/version/{}/merchant/{}/session/{}'.format(version, self.merchant_id, session_id)
        method = 'PUT'
        data = {
            'sourceOfFunds': {
                'type': 'CARD',
                'provided': {
                    'card': {
                        'number': card_number,
                        'expiry': {
                            'month': expiry_month,
                            'year': expiry_year,
                        }
                    }
                }
            }
        }
        return self._request(path, method, data)

    ##############################
    #
    # Tokenization APIs
    #
    ##############################

    def create_token(self, session_id):
        path = 'api/rest/version/{}/merchant/{}/token'.format(version, self.merchant_id)
        method = 'POST'
        data = {
            'session': {
                'id': session_id,
            }
        }
        return self._request(path, method, data)

    def update_token(self):
        pass

    def delete_token(self, token):
        path = 'api/rest/version/{}/merchant/{}/token/{}'.format(version, self.merchant_id, token)
        method = 'DELETE'
        data = {}
        return self._request(path, method, data)

    def retrive_token(self, session_id, token):
        path = 'api/rest/version/{}/merchant/{}/token/{}'.format(version, self.merchant_id, token)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def search_tokens(self, card_number):
        path = 'api/rest/version/{}/merchant/{}/tokenSearch'.format(version, self.merchant_id)
        method = 'GET'
        data = {
            'query': json.dumps({"EQ":["sourceOfFunds.provided.card.number", str(card_number)]})
        }
        return self._request(path, method, data)

    ##############################
    #
    # Transaction APIs
    #
    ##############################

    def authorize(self, session_id, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'AUTHORIZE',
            'order': {
                'currency': currency,
                'amount': amount,
            },
            'session': {
                'id': session_id,
            },
        }
        return self._request(path, method, data)

    def authorize_with_3ds(self, _3ds_secure_id, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'AUTHORIZE',
            'order': {
                'currency': currency,
                'amount': amount,
            },
            '3DSecureId': _3ds_secure_id,
            'sourceOfFunds': {
               'provided': {
                   'card': {
                       'nameOnCard': 'xx',
                       'number': '512345xxxxxx0008',
                   },
               },
               'type': 'CARD',
            },
            # 'sourceOfFunds': {
            #     'provided': {
            #         'card': {
            #             'expiry': {
            #                 'month': 5,
            #                 'year': 21,
            #             },
            #             'nameOnCard': 'xx',
            #             'number': '5123450000000008',
            #         },
            #     },
            #     'type': 'CARD',
            # },
        }
        return self._request(path, method, data)

    def inquiry_balance(self):
        pass

    def capture(self, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'CAPTURE',
            'transaction': {
                'currency': currency,
                'amount': amount,
            },
        }
        return self._request(path, method, data)

    def pay(self, session_id, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'PAY',
            'order': {
                'currency': currency,
                'amount': amount,
                'reference': str(uuid.uuid4()),
            },
            'session': {
                'id': session_id,
            },
            'transaction': {
                'reference': str(uuid.uuid4()),
            }
        }
        return self._request(path, method, data)

    def pay_with_token(self, order_id, transaction_id, amount, currency, token):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'PAY',
            'order': {
                'currency': currency,
                'amount': amount,
                'reference': str(uuid.uuid4()),
            },
            'transaction': {
               'reference': str(uuid.uuid4()),
            },
            'sourceOfFunds': {
                'token': token,
            },
        }
        return self._request(path, method, data)

    def auth_with_token(self, order_id, transaction_id, amount, currency, token):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'AUTHORIZE',
            'order': {
                'currency': currency,
                'amount': amount,
                'reference': str(uuid.uuid4()),
            },
            'transaction': {
               'reference': str(uuid.uuid4()),
            },
            'sourceOfFunds': {
                'token': token,
            },
        }
        return self._request(path, method, data)

    def pay_with_3ds(self, _3ds_id, order_id, transaction_id, amount, currency, token):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'PAY',
            'order': {
                'currency': currency,
                'amount': amount,
                'reference': str(uuid.uuid4()),
            },
            'transaction': {
               'reference': str(uuid.uuid4()),
            },
            '3DSecureId': _3ds_id,
            'sourceOfFunds': {
                'token': token,
            },
            # 'sourceOfFunds': {
            #     'provided': {
            #         'card': {
            #             'expiry': {
            #                 'month': 5,
            #                 'year': 21,
            #             },
            #             'nameOnCard': 'xx',
            #             'number': '5123450000000008',
            #         },
            #     },
            #     'type': 'CARD',
            # },
        }
        return self._request(path, method, data)

    def referral(self):
        pass

    def refund(self, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'REFUND',
            'transaction': {
                'currency': currency,
                'amount': amount,
                'reference': transaction_id,
            },
        }
        return self._request(path, method, data)

    def retrive_order(self, order_id):
        path = 'api/rest/version/{}/merchant/{}/order/{}'.format(version, self.merchant_id, order_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def retrive_transaction(self, order_id, transaction_id):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def update_authorization(self):
        pass

    def verify(self, order_id, transaction_id, card_number, security_code, expiry_month, expiry_year):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'VERIFY',
            'order': {
                'currency': 'SGDD',
            },
            'sourceOfFunds': {
                'type': 'CARD',
                'provided': {
                    'card': {
                        'number': card_number,
                        'securityCode': security_code,
                        'expiry': {
                            'month': expiry_month,
                            'year': expiry_year,
                        }
                    }
                }
            }
        }
        return self._request(path, method, data)

    def void(self, order_id, transaction_id, target_transaction_id, amount):
        path = 'api/rest/version/{}/merchant/{}/order/{}/transaction/{}'.format(version, self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'VOID',
            'transaction': {
                'targetTransactionId': target_transaction_id,
                'reference': transaction_id,
            },
            'order': {
                'amount': amount,
            },
        }
        return self._request(path, method, data)
