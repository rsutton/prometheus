

def print_dict(dict_obj):
    for k in dict_obj.keys():
        print("\t{}: {}".format(k, dict_obj.get(k)))
