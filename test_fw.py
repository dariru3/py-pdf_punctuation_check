import unicodedata
import re

def check_full_width(text):
    temp_set = set()
    full_status = ['W', 'F', 'A']
    for char in text:
        status = unicodedata.east_asian_width(char)
        if status not in full_status:
            temp_set.add(char)
    if temp_set == set():
        temp_set = "empty"
    print("Check 1:", temp_set)
    return temp_set

def check_full_width2(text):
    pattern = re.compile("[\uFF01-\uFF5E]+")
    temp_set = set()
    for char in text:
        if pattern.search(char) is not None:
            temp_set.add(char)
    if temp_set == set():
        temp_set = "empty"
    print("Check 2:", temp_set)
    return temp_set

text = "™㎎㎏㎚㎛㎜㎝㎞㎟㎠㎢㎣㎤㎦㎽㎾㎿ℓ№™₤…ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ△"
print("text len:", len(text))

check_full_width(text)
check_full_width2(text)
