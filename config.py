import yaml
# Read YAML file
with open("settings.yaml", 'r') as stream:
    settings = yaml.safe_load(stream)