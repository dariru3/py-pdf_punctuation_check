import unittest
from main import check_full_width, get_positions, handle_matches, rects_are_equal, add_highlight_annot

class TestFullWidthFunctions(unittest.TestCase):
    
    def test_check_full_width(self):
        full_width_chars = ['／', '％', '’', '（', '）']
        file_path = "output_file.txt"
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        full_width_summary = []
        results = check_full_width(file_content, full_width_summary)
        for char in results:
            self.assertIn(char, full_width_chars, f'Expected {char} to be in {full_width_chars}')

if __name__ == '__main__':
    unittest.main()