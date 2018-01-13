import os
from datetime import datetime, date


def print_dict(dict_obj):
    for k in dict_obj.keys():
        print("\t{}: {}".format(k, dict_obj.get(k)))


def file_age(pathname):
    mtime = os.path.getmtime(pathname)
    delta = date.today() - datetime.fromtimestamp(mtime).date()
    return delta.days
