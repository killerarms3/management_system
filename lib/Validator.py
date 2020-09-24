from django.core.exceptions import ValidationError
def ValidateOrganization(Model, field_name, query, get_or_create=False):
    # query = '[機構]-[部門/單位]'
    status = str()
    messages = list()
    organization = None
    try:
        querys = query.split('-')
        if len(querys) == 2:
            if get_or_create:
                try:
                    Model(name=querys[0], department=querys[1]).full_clean()
                    organization, created = Model.objects.get_or_create(name=querys[0], department=querys[1])
                except ValidationError as err:
                    status = 'Failed'
                    messages.extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            else:
                try:
                    organization = Model.objects.get(name=querys[0], department=querys[1])
                except Model.DoesNotExist:
                    status = 'Falied'
                    messages.append('%s: 找不到此機構' % (field_name))

        else:
            status = 'Falied'
            messages.append('%s: 只接受[機構]-[部門/單位]格式' % (field_name))
    except AttributeError:
        # 'NoneType' object has no attribute 'split'
        status = 'Falied'
        messages.append('%s: 此欄位必填' % (field_name))
    return status, messages, organization