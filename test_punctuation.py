from main import check_punctuation_patterns

def testPunctuation():
    test_sentences = """
    It's me . Hi!
    Are you not entertained??
    He said, “This needs a closing double quote.
    Do not forget to close (parenthesis!!
    And ‘single quotes too.
    """
    test_summary = []
    errors = check_punctuation_patterns(test_sentences, test_summary)
    print(f"errors: {test_summary}")

if __name__ == '__main__':
    testPunctuation()