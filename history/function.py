from .models import History
from django.contrib.auth.models import User
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import datetime
from django.forms.models import model_to_dict
from itertools import chain

# 將object(一筆資料)裡的欄位名稱以及對應的值，轉成字典的型態輸出
def object_to_dict(object):
    opts = object._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        # 將object_id去除
        if f.name == 'id':
            continue
        data[f.name] = str(f.value_from_object(object))
    # solution of many to many field
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(object)]
    return data

# 增加一筆紀錄的操作log到history
def log_addition(user, app_label, model, object_id, action_flag, field_dict, previous_dict):
    '''    
    user =          使用者；Object
    app_label =     小寫app的名稱(ex: 'contract')；字串
    model =         小寫的model名稱(ex: 'order')；字串
    object_id =     該筆紀錄的id；數值
    action_flag =   執行的操作代號，具體名稱寫在function中以字典儲存；字元
    fields_dict =   當前(修改後)的欄位名稱以及對應的值，若是執行的操作為刪除，則直接給予一個空的字典；字典
    previous_dict = 修改前的欄位名稱以及對應的值，若是執行的操作為新增，則直接給予一個空的字典；字典
    '''
    action_flag_dict = {'1': 'add', '2':'change', '3':'delete', '4':'recovery'} # action_flag字典
    content_type = ContentType.objects.get(app_label=app_label, model=model) # 取得contentType
    temp_message = {}
    change_message = {}
    temp_message['fields'] = field_dict
    temp_message['previous'] = previous_dict
    change_message[action_flag_dict[action_flag]] = temp_message
    '''change_message 結構
    change_message = {
        'action':{
            'fields':{
                'attribute1':'value1',
                'attribute2':'value2',
                ......
            },
            'previous':{
                'attribute1':'pre_value1',
                'attribute2':'pre_value2',
                ......
            }
        }
    }
    '''
    History.objects.create( # 新增一筆log至history
        user = user,
        content_type = content_type,
        object_id = object_id,
        action_flag = action_flag,
        change_message = change_message, # 儲存時會把字典轉成字串
        date = datetime.datetime.today()
    )

# 封裝action:change所需的程式
def Update_log_dict(self, form):
    pre_obj = self.get_object() # 取得被操作的紀錄的當前object
    pre_dict = object_to_dict(pre_obj) # 轉成dictionary
    self.object = form.save() # 因為重寫了UpdateView裡的form_valid，把儲存修改的程式移至此，以方便取得修改前後的欄位值
    obj =  self.get_object() # 取得修改後的object
    dict = object_to_dict(obj) # 轉成dictionary
    return obj.id, dict, pre_dict # 回傳 id, 修改前後字典

# 封裝action:change所需的程式，大致步驟與上面的函式相同
def Create_log_dict(self, form, model):    
    self.object = form.save()
    obj =  self.object
    # obj =  model.objects.all().order_by('-id').first() # 取得最新新增的object
    dict = object_to_dict(obj)
    return obj.id, dict

# change_message 是以字串儲存在database，因此若要轉換成dictionsry以便後續復原功能操作，在某些欄位可能會遇到一些問題
# 例如：備註欄為是以TEXT field 型態儲存，若是其內容中含有用來切割字串的字元(EX:':{', ',', "'", ':'...)，都有可能造成切割字串時出現問題
def message_transfer(change_message):
    
    test = change_message[1:-1] # 將最外圈的引號去除    
    test_list = test.split(':{') # 以':{'將字串分開來分成各部分所需的元素
    first_el = test_list[0] # 將最前面的action存進first_el
    second_el = test_list[1] # 將中間的fields存進second_el    
    third_el = test_list[2] # 將fields資料內容放進third_el    
    fourth_el = third_el[-9:] # 將previous存進fourth_el    
    fifth_el = test_list[3] # 將previous資料內容放進fifth_el    
    clear_third_el = third_el[:-11] # 把third_el前後的雜訊清除    
    clear_fifth_el = fifth_el[:-2] # 把fifth_el前後的雜訊清除

    recover_dict = {}
    temp_dict = {}

    make_fields_list = clear_third_el.split(',')
    make_pre_list = clear_fifth_el.split(',')
    fields_dict = {}
    pre_dict = {}

    for fields_dict_el, pre_dict_el in zip(make_fields_list, make_pre_list):
        fields_dict_list = fields_dict_el.split(':')
        pre_dict_list = pre_dict_el.split(':')
        fields_key = fields_dict_list[0]
        fields_value = fields_dict_list[1]
        pre_key = pre_dict_list[0]
        pre_value = pre_dict_list[1]
        fields_dict[fields_key[1:-1]] = fields_value[1:-1]
        pre_dict[pre_key[1:-1]] = pre_value[1:-1]
    # last step
    temp_dict[second_el[1:-1]] = fields_dict
    temp_dict[fourth_el[1:-1]] = pre_dict
    recover_dict[first_el[1:-1]] = temp_dict
    # structure of recover_dict
    '''
    recover_dict = {
        'add':{
            'fields':{
                'attribute1':'value1',
                'attribute2':'value2',
                ......
            },
            'previous':{
                'attribute1':'pre_value1',
                'attribute2':'pre_value2',
                ......
            }
        }
    }
    fields表示為當前(修改後)資料的值
    previous則為修改前的值
    '''
    # 比較前後差異並將其找出
    # for flag in recover_dict['add']['fields'].keys():
    #     if recover_dict['add']['fields'][flag] != recover_dict['add']['preious'][flag]:
    #         print(flag+': '+recover_dict['add']['fields'][flag])
    return recover_dict
    