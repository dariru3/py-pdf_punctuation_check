from main import check_punctuation_patterns

def testPunctuation():
    test_sentence = """
    Hello World!!
    It's me . Hi!
    Are you not entertained??
    """
    test_summary = []
    errors = check_punctuation_patterns(test_sentence, test_summary)
    # print(errors)
    print(f"errors: {test_summary}")

if __name__ == '__main__':
    testPunctuation()