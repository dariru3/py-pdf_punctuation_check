import unittest
from main import check_punctuation_patterns

class PunctuationPatternsTestCase(unittest.TestCase):
    def test_check_punctuation_patterns(self):
        # Test case 1: Provide a text with no punctuation errors
        text1 = "This is a sample text without any punctuation errors."
        summary1 = []
        expected_result1 = set()
        self.assertEqual(check_punctuation_patterns(text1, summary1), expected_result1)
        self.assertEqual(summary1, [])

        # Test case 2: Provide a text with some punctuation errors
        text2 = "This is a sample text with punctuation errors , like space before and after punctuation. And repeated.."
        summary2 = []
        expected_result2 = [
            {'char': ' , ', 'count': 1, 'description': 'Space before and after punctuation'},
            {'char': '.', 'count': 1, 'description': 'Same punctuation is used twice in a row'}
        ]
        self.assertEqual(check_punctuation_patterns(text2, summary2), expected_result2, f"Expected {summary2} to be equal to {expected_result2}")
        self.assertEqual(summary2, [
            {'char': ' , ', 'count': 1, 'description': 'Space before and after punctuation'},
            {'char': '.', 'count': 1, 'description': 'Same punctuation is used twice in a row'}
        ])

if __name__ == '__main__':
    unittest.main()
