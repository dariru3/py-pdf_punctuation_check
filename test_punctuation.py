from main import check_punctuation_patterns

def testPunctuation():
    test_sentence = "(Hello World! (Is it not great?"
    test_summary = []
    errors = check_punctuation_patterns(test_sentence, test_summary)
    print(errors)
    print(f"errors: {test_summary}")

if __name__ == '__main__':
    testPunctuation()

import re

def has_repeated_punctuation(text):
    pattern = re.compile(r"([.,;:?!'\[\]{}()“”‘’&%$¥—-])\1")
    match = pattern.search(text)
    return match is not None

def test_repeated_punctuation():
    test_sentence = "hello??"
    if has_repeated_punctuation(test_sentence):
        print("The sentence has repeated punctuation.")
    else:
        print("The sentence does not have repeated punctuation.")

if __name__ == '__main__':
    pass
    #test_repeated_punctuation()
