import time
from datetime import datetime, timedelta
from json import loads
from PyInquirer import prompt, Separator
import jwt
from cxmaintain.config import Config
from sys import exit
# To-DO: Assumption is SSL/TLS is enabled. Port 80 is currently unsupported.

class Auth(Config):
    """
    Perform all Authentication tasks here!
    """
    def __init__(self, verbose):
        print("Auth Verbose: ", verbose)
        super().__init__(verbose)
        self.verify = True
        self.token = None
        self.host = "localhost"
        self.auth_provider = "Application"
        self.auth_payload = payload = 'username={0}&password={1}&grant_type=password&scope={2}&client_id={3}&client_secret=014DF517-39D1-4453-B7B3-9930C563627C'
        self.client_id = str()
        # Default to CxAC Only API Scope
        self.scope = "sast_rest_api"
        self.logger.info("Login scope is: {0}".format(self.scope))
        self.base_url = "https://{0}/cxrestapi/auth{1}"
        self.logger.info("Base URI: {0}".format(self.base_url))
        self.headers = {
            'Accept': 'application/json;v=1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def set_host(self):
        """
        Set the URL Checkmarx CxSAST v9.0
        """
        host_questions = [
            {
                'type': 'input',
                'qmark': 'Checkmarx Host',
                'message': '(Default localhost).Checkmarx URL, IP, Host-Name or FQDN (Ex: sast.checkmarx.au):',
                'name': 'host',
                'default': 'sast.cx.au'
            },
        ]
        host_answers = prompt(host_questions)
        self.logger.info("Host Answers")
        self.logger.info(host_answers)
        if self.verbose:
            print(host_answers)
            print("Host: {0}".format(host_answers['host']))
            self.logger.info("Host: {0}".format(host_answers['host']))
        self.host = host_answers['host']

    def set_scope(self):
        scope_questions = [
            {
                'type': 'checkbox',
                'qmark': 'Login Scope',
                'message': 'Select login scope. Access Control is selected by default',
                'name': 'Privileges Choice',
                'choices': [
                    Separator('*-* Select Login scope *-*'),
                    {
                        'name' : 'Checkmarx Access Control Module',
                        'checked': True
                    },
                    {
                        'name': 'Checkmarx CxSAST Module',
                    }
                ]
            }
        ]
        scope_map = {
            'Checkmarx CxSAST Module': 'sast_rest_api',
            'Checkmarx CxSAST Module': 'sast-permissions'
            'Open ID Configuration''open_id',
            'Checkmarx Access Control API': 'access_control_api',
            'Checkmarx Access Control Permissions': 'access-control-permissions'
        }

        # Uncomment below if additional scope is reuquired.
        # This module defaults to using just he access control api.
        # scope_answers = prompt(scope_questions)
        # scope_answers = scope_answers['Privileges Choice']
        # self.scope = " ".join([scope_map[scope_answer] for scope_answer in scope_answers if scope_answer in scope_map])
        # self.logger.info("Scope info")
        # self.logger.info(scope_answers)
        if not self.scope:
            self.scope = 'sast_rest_api'

    def check_connection(self, url):
        """
        Check Connection to target host
        """
        try:
            response = self.session.get(url=url, verify=True)
            if response.ok:
                return True
        except Exception as err:
            # Try SSL verify off and check
            try:
                response = self.session.get(url=url, verify=False)
                return False
            except Exception as err:
                self.logger.info("error in connecting to: {0}", url)
                print("Unable to connect to {0}. Please check if host is accessible/available.".format(self.host))
                exit()

    def check_ssl_verification(self):
        # Check SSL, If Self-Signed set SSL-Verify false with a prompt
        url = self.base_url.format(self.host, "/AuthenticationProviders")
        #To-DO: Log here
        if not self.check_connection(url):
            print("SSL Validation Error occurred")
            ssl_questions = [
                {
                    'type': 'confirm',
                    'qmark': 'SSL Verification',
                    'message': 'Self-Signed Cert detected. Turn off SSL Certificate verification?',
                    'name': 'disableSslVerify'
                }
            ]
            ssl_answer = prompt(ssl_questions)
            self.logger.info("SSL Options")
            self.logger.info(ssl_answer)
            if self.verbose:
                print(ssl_answer)
            self.verify = not ssl_answer['disableSslVerify']

    def set_client_id(self):
        # To-DO: Client Secret
        client_id_questions = [
            {
                'type': 'input',
                'qmark': 'CxREST API Client for use',
                'message': 'Default is resource_owner_client. Custom client use is to be implemented.',
                'name': 'client_id',
                'default': 'Use Default Client'
            }
        ]
        client_id_map = {
            'Use Default Client': 'resource_owner_client'
        }
        # Uncomment this only if using a non-default custom client.
        # This will promt for the client ID on the console.
        # client_id_answers = prompt(client_id_questions)
        # self.client_id = client_id_map[client_id_answers['client_id']]
        # self.logger.info("ClientID: {0}".format(self.client_id))
        # Comment this below if uncommenting above
        if self.verbose:
            print("client ID: ", self.client_id)
            self.logger.info("Client ID: {0}".format(self.client_id))
        self.client_id = client_id_map['Use Default Client']

    def ask_domain(self):
        """
        Check available domains configured on Checkmarx Access Control Module
        """
        auth_providers_url = self.base_url.format(self.host, "/AuthenticationProviders")
        response = self.session.request('GET', url=auth_providers_url, verify=self.verify)
        if not response.ok:
            raise Exception
        # Write providers
        auth_providers = response.json()

        auth_provider_questions = [
            {
                'type': 'checkbox',
                'qmark': 'Authentication Providers',
                'message': 'Select login scope. Access Control is selected by default',
                'name': 'provider',
                'choices': [
                    Separator('*-* Select Authentication providers *-*'),
                ],
                'validate': lambda answer: 'You must choose one.' if not len(answer) == 1 else True
            }
        ]
        # Setting a static index here.
        for auth_provider in auth_providers:
            auth_provider_questions[0]['choices'].append({'name': auth_provider['name']})

        # Default to Application user if no option is chosen.
        # When choosing options, User has to hit space-bar.
        auth_provider_answers = prompt(auth_provider_questions)
        if len(auth_provider_answers['provider']) == 0:
            auth_provider_answers['provider'].append('Application')

        self.auth_provider = auth_provider_answers['provider'][0]

        if self.verbose:
            print("Using Auth Provider: {0}".format(self.auth_provider))
            self.logger.info("Auth Provider chosen")
            self.logger.info(self.auth_provider)

    def ask_creds(self):
        domain_append = 'CxSastUser'
        if self.auth_provider != 'Application':
            domain_append = "{0}\\".format(self.auth_provider)
        auth_questions = [
                            {
                                'type': 'input',
                                'qmark': 'Credentials',
                                'message': 'Checkmarx Username:',
                                'name': 'username',
                                'default': domain_append
                            },
                            {
                                'type': 'password',
                                'message': 'Password:',
                                'name': 'password'
                            }
                        ]
        self.logger.info("Authentication")
        return prompt(auth_questions)

    def perform_auth(self, save_config=False):
        """
        Setting default scope to use just the AC Module
        """
        # Set Host, Scope and Client type
        self.set_host()
        self.set_scope()
        self.set_client_id()
        self.check_ssl_verification()
        self.ask_domain()
        creds = self.ask_creds()
        ###################
        # Do not log this #
        ###################
        payload = self.auth_payload.format(creds['username'], creds['password'], self.scope, self.client_id)
        auth_url = self.base_url.format(self.host, "/identity/connect/token")
        try:
            token_type, token_raw, token_decoded = None, None, None
            response = self.session.request("POST", auth_url, headers=self.headers, data = payload, verify=self.verify)
            if response.ok:
                self.logger.info("Authentication successful.")
                token_type, token_raw = response.json()['token_type'], response.json()['access_token']
                self.token = "{0} {1}".format(token_type, token_raw)
                # Decode token and print expiry
                # Do not save token to disk
                token_decoded = jwt.decode(token_raw, options={'verify_signature': False})
                print("Token expires by: {0} ({1} Hours).".format(
                    datetime.fromtimestamp(token_decoded['exp']),
                    int((int(token_decoded['exp']) - int(time.time()))/(3600))
                ))
                self.logger.info("Token expires by: {0} ({1} Hours).".format(
                    datetime.fromtimestamp(token_decoded['exp']),
                    int((int(token_decoded['exp']) - int(time.time()))/(3600))
                ))
                if save_config:
                    meta = {'token':token_raw, 'auth_time': token_decoded['auth_time'] , 'exp': token_decoded['exp'] , 'team': token_decoded['team']}
                    self.save_token(meta=meta)
                    print("Token Config saved at' : self.token_config")
                    meta = {'host': self.host, 'ssl_verify': self.verify, 'auth_provider': self.auth_provider}
                    self.save_cxconfig(meta=meta)
                    print("Cx Config saved at' : self.cx_config")
                    self.logger.info("Cx Config saved at' : self.cx_config")
            else:
                # To-DO: Log Error
                print("Authentication unsuccessful.")
                if self.verbose:
                    print(response.text)
                    self.logger.error(response.text)

        except requests.exceptions.RequestException as http_err:
            # To-Do: Log error
            print(" General Error occurred. Status: {0}".format(response.status_code))
            self.logger.error(" General Error occurred. Status: {0}".format(response.status_code))
            self.logger.error("Details: {0}".format(response.text))
        creds = {}
