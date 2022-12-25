import math

def expand_str(str, end_str, final_len):
    """ Expand the file name string up to the maximum width of the pad """
    str_maxlength = math.floor(final_len-len(end_str) * 4.0/5.0)
    if len(str) > str_maxlength:
        split_str = str.split(".")
        if len(split_str) > 1:
            name = '.'.join(split_str[:-1])
            extension = split_str[-1]
        else:
            name = ''.join(split_str[0])
            extension = ''
        max_name = str_maxlength - len(extension) - 8
        name = name[:max_name] + '~'
        if str.find('.') == -1:
            str = name
        else:
            str = name + "." + extension
    padding = final_len - len(str) - 3
    return " " + str + end_str.rjust(padding, ' ') + " "

first_str = 'qt_compose_cache_little_endian_eaa24ac0b722499da30a9fa9f263301f'
second_str = 'event-sound-cache.tdb.eaa24ac0b722499da30a9fa9f263301f'
result = expand_str(second_str, '165.4 KB', 50)
print(result)
print(len(result))