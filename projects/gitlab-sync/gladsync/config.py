from pathlib import Path
import gitlab
import sys
import os
import yaml

# Default config details. Overwritten by values in the config file, if they are given.
defaults = {
    'gl_url': 'https://gitlab.com',
    'gl_pat': '',
    'ad_url': '',
    'ad_user': '',
    'ad_pass': '',
    'access_level': gitlab.const.AccessLevel.DEVELOPER
}


class Config:
    def __init__(self, config_path: Path):
        '''
        Parse and validate config data from .ini config files. (TODO add other formats?)
        '''
        self.validate_path(config_path)

        config = self.parse(config_path)

        # set this object's attrs to default values unless overwritten
        # errors are collected and thrown after checking all values
        missing_values = []
        for key in defaults.keys():
            try:
                # Set config file value if one is provided
                setattr(self, key, config[key])
            except KeyError as e:
                if not defaults[key]:
                    # if no default exists, throw error
                    missing_values.append(key)
                else:
                    # set attr to default value as last resort
                    setattr(self, key, defaults[key])
        
        if missing_values:
            sys.exit(f"Required values not found in '{config_path}': {missing_values}")


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

        return config

# testing
if __name__ == "__main__":
    print(os.getcwd())
    Config('test.yaml')