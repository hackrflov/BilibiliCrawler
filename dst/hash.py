import hashlib
import itertools

def get_subsets(mother_set):
    result = []
    for i in range(1,len(mother_set)+1):
        for j in itertools.combinations(mother_set,i):
            result.append(list(j))
    return result

if __name__ == '__main__':
    '''
    params = [
        ['appkey','1d8b6e7d45233436'],
        ['build','510000'],
        ['mobi_app','android'],
        ['oid','12816363'],
        ['plat','2'],
        ['platform','android'],
        ['pn','1'],
        ['ps','20'],
        ['sort','0'],
        ['ts','1501917765'],
        ['type','1'],
    ]
    params = [
        ['aid','12816363'],
        ['appkey','1d8b6e7d45233436'],
        ['build','510000'],
        ['from','7'],
        ['mobi_app','android'],
        ['plat','0'],
        ['platform','android'],
        ['ts','1501917764'],
    ]
    '''
    params = [
        ['appkey','12737ff7776f1ade'],
        ['id','12869982'],
        ['type','json'],
    ]
    subset = get_subsets(params)
    for s in subset:
        data = ''
        for (key, value) in s:
            data += '%s=%s&' %(key,value)
        data = data[:-1]#.upper()
        m = hashlib.md5()
        m.update(data)
        sign = m.hexdigest()
        print data, sign
        if sign == '738345446e812e4a24fca24fe8c02a87':
            print sign

