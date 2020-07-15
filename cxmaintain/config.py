import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
from os.path import exists as path_exists
from os.path import isdir
from os.path import isfile
from os import mkdir as create_directory
import yaml
from cxdir.utils.connections import Connection
# To-Do: De-duplicate read-write methods to a factory
# Reserving this for now as a future todo.


class Config(Connection):
    """
    Config depends on connection to make a predictable MRO only.
    However, MRO is being abused here to make connection available universally.
    """
    def __init__(self, verbose):
        super().__init__(verbose)
        self.verbose = verbose
        self.config_path = Path.joinpath(Path().home(), ".cx")
        # Logger
        self.log_path = Path.joinpath(self.config_path, "logs")
        self.logfile_path = self.log_path / "cxdir.log"

        # Setup paths
        self.token_config = self.config_path / "cxdirToken.yaml"
        self.cx_config = self.config_path / "cxdir.yaml"
        # Setting this as default for LDAP Provider ID
        # This may require clean-up if multiple LDAP connections are to be used.
        self.ldap_provider_id = None
        self.ldap_providers = None
        # Enable this first - So that log file is available or created
        self.check_path()
        # Logger
        self.logger = logging.getLogger('CxDir')
        logging.basicConfig(handlers=[RotatingFileHandler(self.logfile_path, maxBytes=100000, backupCount=10)],
                            level=logging.DEBUG if self.verbose else logging.INFO,
                            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                            datefmt='%Y-%m-%dT%H:%M:%S'
                            )

    def check_path(self):
        """
        Implicit check
        Touch and create yaml file in <user_home_dir>/.cx/ac.yaml
        Touch and create yaml file in <user_home_dir>/.cx/team.yaml
        """
        # To-Do: Loop over as the list has grown. Make this more pythonic.
        config_dirs = [self.config_path, self.log_path]
        config_files = [ self.token_config, self.cx_config, self.logfile_path]

        try:
            # Config Dirs
            for config_dir in config_dirs:
                if not path_exists(config_dir) or not isdir(config_dir):
                    if self.verbose:
                        print("Creating config directory: {0}".format(config_dir))
                    create_directory(config_dir)
                else:
                    if self.verbose:
                        print("Directory exists at: {0}".format(config_dir))

            # Config Files
            for config_file in config_files:
                if not path_exists(config_file):
                    if self.verbose:
                        print("creating config file at: {0}".format(
                            config_file))
                    Path(config_file).touch()
                else:
                    if self.verbose:
                        print("Config file exists at: {0}".format(config_file))

            if self.verbose:
                print("Config directory and files exist already")
            return True

        except Exception as err:
            print("Config files do no exist. Please run cxclient init OR cxclient login --save.")
            self.logger.info("Config files failure or absense of token.")
            if self.verbose:
                print(err)
            return

    def save_cxconfig(self, meta):
        """
        Save CxServer config - SSL, Host
        """
        with open(self.cx_config, 'w') as cx_config_writer:
            print("Saving CxConfig at: {0}".format(self.cx_config))
            self.logger.info("Saving CxConfig at: {0}".format(self.cx_config))
            file_dump = yaml.dump(meta, cx_config_writer)

    def save_token(self, meta):
        """
        Save OAuth Token to Configuration directory
        """
        # Check config directory exists
        self.check_path()
        # Always write mode to Update from Cx.
        with open(self.token_config, 'w') as token_writer:
            print("Token is at: {0}".format(self.token_config))
            self.logger.info("Token is at: {0}".format(self.token_config))
            file_dump = yaml.dump(meta, token_writer)

    def read_token(self):
        """
        Read token from config
        """
        self.check_path()
        try:
            with open(self.token_config, 'r') as token_reader:
                print("Reading token from disk: {0}".format(self.token_config))
                # Do not use yaml.load - To avoid Arbitrary Code Execution through YAML.

                data = yaml.full_load(token_reader)
                # Token is not expired
                assert(data)
                time_gap = int(data['exp']) - int(time.time())
                if self.verbose and time_gap > 0:
                    print("Token is valid for: {0} minutes.".format(
                        int(time_gap/60)))
                    self.logger.info(
                        "Token is valid for: {0} minutes.".format(int(time_gap/60)))
                if self.verbose and time_gap <= 0:
                    print("Token expired OR is invalid. Please try login with --save")
                    self.logger.error(
                        "Token expired OR is invalid. Please try login with --save")
                return data['token']
        except Exception as err:
            if self.verbose:
                print("File is missing. Please try init, then login with --save flag.")
                self.logger.debug(
                    "File is missing. Please try init, then login with --save flag.")
                raise FileExistsError

            self.logger.error("Error in reading token")
            print("Error in reading token")
            pass

    def read_cx_config(self):
        """
        Read CxConfig from config
        """
        with open(self.cx_config, 'r') as cx_config_reader:
            # Do not use yaml.load - To avoid Arbitrary Code Execution through YAML.
            print("Reading config from here: {0}".format(self.cx_config))
            self.logger.info(
                "Reading config from here: {0}".format(self.cx_config))
            return yaml.full_load(cx_config_reader)

