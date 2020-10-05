from django.apps import apps
from language.models import Code
from django.contrib.contenttypes.models import ContentType

def getlabels(AppName, ModelName):
    field_tags = dict()
    Model = apps.get_model(AppName, ModelName)
    field_names = [field.name for field in Model._meta.fields]
    contenttype = ContentType.objects.get(app_label=AppName, model=ModelName)
    for field_name in field_names:
        field_tags[field_name] = field_name
        codes = Code.objects.filter(content_type=contenttype, code=field_name)
        if codes:
            field_tags[field_name] = codes[0].name
    return field_tags