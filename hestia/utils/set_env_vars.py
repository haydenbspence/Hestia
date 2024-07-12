import os

import toml

config_file_path = '../../config.toml'

def set_env_vars(config_file_path: str):
    config = toml.load(config_file_path)
    motherduck_token = config['tokens']['motherduck']
    os.environ['MOTHERDUCK_TOKEN'] = motherduck_token
    motherduck_token_from_env = os.getenv('MOTHERDUCK_TOKEN')

    return motherduck_token_from_env

set_env_vars(config_file_path)