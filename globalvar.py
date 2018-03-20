def _init():#初始化
    global _global_dict
    _global_dict = {}

def set_value(key,value):#获取值
    _global_dict[key] = value


def get_value(key,defValue=None):#赋值
    try:
        return _global_dict[key]
    except KeyError:
        return defValue