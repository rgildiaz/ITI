from pathlib import Path
import gitlab
import sys
import os
import yaml
import logging

# Default config details. Overwritten by values in the config file if they are given.
# Since attrs are generated automatically, add more key/value pairs here if more config data needed.
# Keys without values are required.
defaults = {
    'gl_url': 'https://gitlab.com',
    'gl_pat': '',
    'gl_root': '',
    'ad_url': '',
    'ad_user': '',
    'ad_pass': '',
    'access_level': gitlab.const.AccessLevel.DEVELOPER,
}


class Config:
    def __init__(self, config_path: Path, test: bool, verbose: bool, std_out: bool):
        '''
        Parse and validate config data from .yaml config files.
        Also, setup a root logger.

        Args:
            config_path (Path) : the path to the .yaml config file to use.
            test (bool) : test mode switch (`True` will make no remote changes).
            verbose (bool) : verbose switch (`True` will print extra information).
            std_out (bool) : standard out print switch (`True` will print to stdout).
        '''
        # setup logging and stdout handler
        # another file handler is setup in self.parse() if a log_file is specified
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        
        # only add the stdout handler if switched.
        if std_out:
            std_handler = logging.StreamHandler(sys.stdout)
            std_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - gladsync (%(module)s) - %(levelname)s - %(message)s')
            std_handler.setFormatter(formatter)
            self.log.addHandler(std_handler)

        # once the std logger is setup, begin config logic.
        self.validate_path(config_path)

        config = self.parse(config_path)
        pwd = os.getcwd()

        # set this object's attrs to default values unless overwritten
        # errors are collected and thrown after checking all values
        missing_values = []
        missing_test_values = []
        for key in defaults.keys():
            try:
                # Will throw error if key is not provided
                if len(str(config[key])) > 0:
                    # Set config file value if one is provided
                    setattr(self, key, config[key])
                else:
                    # set as default if empty value is provided
                    setattr(self, key, defaults[key])
            except KeyError as e:
                # since GL info doesn't matter in test mode, skip GL info if not found
                # TODO REMOVE AD KEYS FROM LIST
                if test and (key in ['gl_url', 'gl_pat', 'gl_root', 'ad_url', 'ad_user', 'ad_pass']):
                    missing_test_values.append(key)
                    continue
                if not defaults[key]:
                    # if no default exists, throw error
                    missing_values.append(key)
                else:
                    # set as default value as last resort
                    setattr(self, key, defaults[key])

        if verbose:
            self.log.debug(f"Config: {self._get_attrs()}")

        # since gitlab values were skipped in test mode above, print warning.
        if missing_test_values:
            self.log.info(
                f"(test) Required values not found in {pwd}/{config_path}: {missing_test_values}")
        if missing_values:
            self.log.error(
                f"Required values not found in {pwd}/{config_path}: {missing_values}")
            sys.exit()
            
        self.log.info('Config complete!')

    def _get_attrs(self) -> dict:
        '''
        Safely get all attributes.

        Returns:
            dict : this object's attributes with sensitive information removed.
        '''
        # the attrs to replace in output
        protected = ['gl_pat', 'ad_pass']
        attrs = self.__dict__.copy()

        for a in protected:
            try:
                # replace the value if it exists
                if attrs[a]:
                    attrs[a] = '(removed from output)'
            except:
                continue

        return attrs

    def validate_path(self, path: Path) -> bool:
        '''
        Ensure the path to the config file is valid. Exit with errors if not.

        Args:
            config_path (Path) : the path to the config file to use.
        Returns:
            bool : whether or not the path is valid.
        '''
        valid = True

        # Path/file validation
        try:
            if not os.path.exists(path):
                self.log.error(f'Path "./{path}" does not exist.')
                valid = False
            elif not os.path.isfile(path):
                self.log.error(
                    f'Object at path "./{path}" is not a file.')
                valid = False
        except TypeError:
            self.log.error(
                f'Path "./{path}" must be of type Path. Type {type(path)} given.')
            valid = False

        if not valid:
            sys.exit("Errors found. Exiting...")

        self.log.debug(f"Path to config file valid: {path}")

        # will always return true or exit in above block
        return valid

    def parse(self, config_file: Path) -> dict:
        '''
        Parse a YAML config file.

        Args:
            config_file (Path) : the path to a YAML config file.
        Returns:
            dict : a dict representation of the given YAML file.
        '''
        conf = ""

        try:
            # read each line to prevent memory issues
            with open(config_file, 'r') as f:
                for line in f:
                    conf += line
        except Exception:
            self.log.error(f'Could not read config file {config_file}')
            sys.exit()

        try:
            config = yaml.safe_load(conf)
        except Exception as e:
            self.log.error(f'Could not load YAML from config file.{conf}')
            sys.exit()

        self.configure_log(config)

        # set access level to the appropriate gitlab.const
        if not config['access_level']:
            config['access_level'] = ""

        config['access_level'] = self.set_access(config['access_level'])

        self.log.info(f'Config file {config_file} parsed')

        return config

    def set_access(self, access: str) -> gitlab.const.AccessLevel:
        '''
        Set gitlab.const.AccessLevel based on parsed config data.

        GUEST: 10
        REPORTER: 20
        DEVELOPER: 30
        MAINTAINER: 40
        OWNER: 50

        Args:
            access (str) : a string representing access level.
        Returns: 
            gitlab.const.AccessLevel : the access level const corresponding to config
        '''

        access_levels = {
            'guest': gitlab.const.AccessLevel.GUEST,
            'reporter': gitlab.const.AccessLevel.REPORTER,
            'developer': gitlab.const.AccessLevel.DEVELOPER,
            'maintainer': gitlab.const.AccessLevel.MAINTAINER,
            'owner': gitlab.const.AccessLevel.OWNER
        }

        # If access cannot be parsed or does not exist, set to default value
        if access:
            try:
                out = access_levels[access.lower()]
            except Exception as e:
                self.log.info(
                    f"Given access level <{access}> not valid. Reverting to default level: {defaults['access_level']}")
                out = defaults['access_level']
        else:
            out = defaults['access_level']

        return out

    def configure_log(self, config):
        '''
        Create a logging.FileHandler() and attach it to self.log if a log_file is specified in the config.

        Args:
            config : a parsed YAML config file
        '''
        if 'log_file' in config:
            try:
                file_handler = logging.FileHandler(config['log_file'])
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    '%(asctime)s - gladsync (%(module)s) - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                self.log.addHandler(file_handler)
                self.log.info(f"Log file '{config['log_file']}' found")
            except Exception as e:
                self.log.error(f'Log file cannot be setup: {e}')
        else:
            self.log.info(f"'log_file' not found in config.")


# testing
if __name__ == "__main__":
    print(os.getcwd())
    Config('test.yaml', True)
