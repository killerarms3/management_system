from django.core.exceptions import ValidationError
from django import forms
import datetime

def ValidateOrganization(Model, field_name, query):
    # query = '[機構]-[部門/單位]'
    status = str()
    messages = list()
    organization = None

    try:
        querys = query.split('-')
        if len(querys) == 2:
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

def TaiwanTelNumber(value):
    # 國內電話號碼格式: [國內電話區號][開放電話號碼](e.g. 0912345678)
    if value[0] != '0':
        raise forms.ValidationError('國內電話請用0開頭')
    if len(value) != 9 and len(value) != 10:
        raise forms.ValidationError('號碼位數錯誤，%d位' % (len(value)))
    if value[:2] == '09':
        raise forms.ValidationError('市內電話不接受09開頭')

def TaiwanMobileNumber(value):
    # 國內電話號碼格式: [國內電話區號][開放電話號碼](e.g. 0912345678)
    if value[:2] != '09':
        raise forms.ValidationError('手機電話請用09開頭')
    if len(value) != 10:
        raise forms.ValidationError('號碼位數錯誤，%d位' % (len(value)))

def InternationalPhoneNumber(contry_code, value):
    # 國際電話號碼格式: [國際電話區號]-[國內電話區號][開放電話號碼](e.g. 886-912345678), [國內電話區號][開放電話號碼]最多11位
    # 位數在4~11之間(包含國內區號)
    if len(value) < 4 and len(value) > 11:
        raise forms.ValidationError('號碼位數錯誤，%d位' % (len(value)))
    if value[0] == '0':
        raise forms.ValidationError('國際電話號碼中的國內區碼，請去掉0')

def ValidateTelNumber(value):
    # 假設0開頭的都是國內電話
    if value:
        digits = value.split('-')
        for idx, digit in enumerate(digits):
            digits[idx] = ''.join([d for d in digit if d.isdigit()])
        if value[0] == '0':
            # 假設此為國內電話 e.g. 0212345678
            digit = ''.join(digits)
            TaiwanTelNumber(digit)
        else:
            # 第一個item為國際電話區號
            country_code = digits[0]
            digit = ''.join(digits[1:])
            if country_code == '886':
                raise forms.ValidationError('國內電話請用[國內電話區號]開頭')
            elif digit:
                InternationalPhoneNumber(country_code, digit)
            else:
                raise forms.ValidationError('國際電話只接受[國際電話區號]-[國內電話區號][開放電話號碼]格式')

def ValidateMobileNumber(value):
    # 手機電話目前只接受國內
    if value:
        digits = value.split('-')
        for idx, digit in enumerate(digits):
            digits[idx] = ''.join([d for d in digit if d.isdigit()])
        if value[0] == '0':
            # 假設此為國內電話
            digit = ''.join(digits)
            TaiwanMobileNumber(digit)
        else:
            raise forms.ValidationError('手機電話目前只接受國內手機格式: [09][開放電話號碼]')


def ValidateDate(value):
    if value:
        try:
            if isinstance(value, datetime.date):
                value = datetime.datetime(value.year, value.month, value.day)
            else:
                value = datetime.datetime.strptime(value, '%Y-%m-%d')
            now = datetime.datetime.now()
            if value > now:
                raise forms.ValidationError('不接受未來日期')
        except ValueError:
            raise forms.ValidationError('日期格式錯誤，只接受"YYYY-MM-DD')

def ValidateAfterDate(before_date, after_date):
    try:
        before_date = datetime.datetime.strptime(str(before_date), '%Y-%m-%d')
        after_date = datetime.datetime.strptime(str(after_date), '%Y-%m-%d')
        if before_date > after_date:
            return False
        else:
            return True
    except ValueError:
        return False
