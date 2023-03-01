from pathlib import Path
import gitlab
import sys
import os
import yaml

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
    'access_level': gitlab.const.AccessLevel.DEVELOPER
}


class Config:
    def __init__(self, config_path: Path, test: bool, verbose: bool):
        '''
        Parse and validate config data from .yaml config files. (TODO add other formats?)

        Args:
            config_path (Path) : the path to the .yaml config file to use.
            test (bool) : test mode switch (`False` will modify GitLab).
            verbose (bool) : verbose switch (`True` will print extra information).
        '''
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
            sys.stdout.write(f"\nConfig: {self._get_attrs()}\n")

        # since gitlab values were skipped in test mode above, print warning.
        if missing_test_values:
            sys.stdout.write(
                f"\n(test) Required values not found in {pwd}/{config_path}: {missing_test_values}\n")
        if missing_values:
            sys.exit(
                f"\nRequired values not found in {pwd}/{config_path}: {missing_values}")
            pass

    def _get_attrs(self):
        '''
        Safely get all attributes.

        Returns:
            dict : this object's attributes with sensitive information removed.
        '''
        # the attrs to replace in output
        protected = ['gl_pat', 'ad_pass']
        # have to make a copy to avoid modifying attrs.
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
                sys.stderr.write(f'Path "./{path}" does not exist.\n')
                valid = False
            elif not os.path.isfile(path):
                sys.stderr.write(
                    f'Object at path "./{path}" is not a file.\n')
                valid = False
        except TypeError:
            sys.stderr.write(
                f'Path "./{path}" must be of type Path. Type {type(path)} given.\n')
            valid = False

        if not valid:
            sys.exit("Errors found. Exiting...")

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
            sys.exit(f'Could not read config file {config_file}')

        try:
            config = yaml.safe_load(conf)
        except Exception as e:
            sys.exit(f'Could not load YAML from config file.\n{conf}')

        # set access level to the appropriate gitlab.const
        config['access_level'] = self.set_access(config['access_level'])

        return config

    def set_access(self, access: str):
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

        # Access level const specifications
        access_levels = {
            'guest': gitlab.const.AccessLevel.GUEST,
            'reporter': gitlab.const.AccessLevel.REPORTER,
            'developer': gitlab.const.AccessLevel.DEVELOPER,
            'maintainer': gitlab.const.AccessLevel.MAINTAINER,
            'owner': gitlab.const.AccessLevel.OWNER
        }

        # If access cannot be parsed, set to first element of dict
        min_access = list(access_levels.items())[0]

        if access:
            try:
                out = access_levels[access.lower()]
            except Exception as e:
                sys.stdout.write(
                    f"Given access <{access}> not valid. Reverting to minimum level: {min_access}")
                # min_access is a tuple, so need to get second element
                out = min_access[1]
        else:
            out = min_access[1]

        return out


# testing
if __name__ == "__main__":
    print(os.getcwd())
    Config('test.yaml', True)
