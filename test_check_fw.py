import unicodedata, re
import unittest

string1 = 'Return to work rate after childcare leave*15 (women/men) 100.0% ／ 50.0％'
string2 = 'Improvement in SMEs’ cash flow（FSA and SMEA)'
string3 = 'Resolving issues of a super-aging society（METI, MHLW, and FSA）'
full_width_chars = ['／', '％', '’', '（', '）']


def check_full_width(text):
    target_set = set()
    full_status = ['W', 'F', 'A']
    pattern = re.compile("[\uFF01-\uFF5E]+")

    excluded_chars = {
        '\u0022',  # Half-width double quote mark (")
        '\u0027',  # Half-width single quote mark/apostrophe (')
        '\u2018',  # Left single quotation mark (‘)
        '\u2019',  # Right single quotation mark (’)
        '\u201C',  # Left double quotation mark (“)
        '\u201D',  # Right double quotation mark (”)
        '\u2014',  # Em dash (—)
    }

    for char in text:
        if char not in excluded_chars:
            status = unicodedata.east_asian_width(char)
            if status in full_status or pattern.search(char):
                target_set.add(char)
    return target_set

class TestCheckFullWidth(unittest.TestCase):
    def test_check_full_width(self):
        test_strings = [string1, string2, string3]
        for string in test_strings:
            with self.subTest(string):
                result_set = check_full_width(string)
                for char in result_set:
                    self.assertIn(char, full_width_chars, f'Expected {char} to be in {full_width_chars}')

# if __name__ == '__main__':
#     unittest.main()

file_path = "output_file.txt"
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

results = check_full_width(file_content)
print(results)