import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management_system.settings')
django.setup()

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import logging
from language.models import Code
import yaml
from django.conf import settings
from collections import OrderedDict


__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)


def dumpdefaultyaml(output_yaml):
    yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))
    yaml_dict = OrderedDict()
    app_labels = {app_label for app_label in settings.INSTALLED_APPS if 'django.contrib' not in app_label}
    for model in apps.get_models():
        if model._meta.app_label in app_labels:
            if model._meta.app_label not in yaml_dict:
                yaml_dict[model._meta.app_label] = OrderedDict()
            if model.__name__ not in yaml_dict[model._meta.app_label]:
                yaml_dict[model._meta.app_label][model.__name__] = OrderedDict()
            for field in model._meta.fields:
                yaml_dict[model._meta.app_label][model.__name__][field.name] = field.name
    with open(output_yaml, 'w') as out_f:
        yaml.dump(yaml_dict, out_f)

def loadtodb(input_yaml):
    with open(input_yaml, 'r') as in_f:
        yaml_dict = yaml.load(in_f, Loader=yaml.FullLoader)
        # 之後改寫
        for app_label in yaml_dict:
            for model in yaml_dict[app_label]:
                contenttype = ContentType.objects.get(app_label=app_label, model=model)
                for field_name in yaml_dict[app_label][model]:
                    code, created = Code.objects.get_or_create(content_type=contenttype, code=field_name)
                    code.name = yaml_dict[app_label][model][field_name]
                    code.save()

def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\

    Usage:
    %(prog)s -i
    """))
    # argument
    parser.add_argument('-i', '--input_yaml', help='default_codes.yaml')
    # parser.add_argument('-o', '--output_yaml', help='filename of the output default_codes.yaml')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    loadtodb(args.input_yaml)

if __name__ == '__main__':
    main()