import yaml


def parse_credentials(path):
    text = open(path).read()
    creds = yaml.safe_load(text)
    return creds

