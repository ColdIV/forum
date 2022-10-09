from collections import OrderedDict

def getPermissionList():
    permissions = OrderedDict()
    permissions['+'] = 'home'
    permissions['f'] = 'forum'
    permissions['a'] = 'admin'
    permissions['*'] = 'everything'

    return permissions