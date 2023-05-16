import unittest
from main import check_punctuation_patterns

def testParethesis():
    test_sentence = "This is missing a (closing parenthesis)."
    test_summary = []
    errors = check_punctuation_patterns(test_sentence, test_summary)
    print(errors)

if __name__ == '__main__':
    testParethesis()
