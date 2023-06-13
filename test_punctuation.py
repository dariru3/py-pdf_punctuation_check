from main import check_punctuation_errors

def testPunctuation():
    test_sentences = """
    It's me . Hi!
    Are you not entertained??
    He said, “This needs a closing double quote.
    Do not forget to close (parenthesis!!
    """
    test_summary = []
    check_punctuation_errors(test_sentences,test_summary)
    print(f"errors: {test_summary}")

if __name__ == '__main__':
    testPunctuation()