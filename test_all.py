import unittest
from unittest.mock import MagicMock
import os
import fitz
from config import config
from main import check_full_width, get_positions, handle_matches, rects_are_equal, add_highlight_annot

def extract_text(input_file:str):
    pdfIn = fitz.open(input_file)
    all_text = ""
    for page in pdfIn:
        text = page.get_text("text")
        all_text += text
    
    with open("output_file.txt", 'w') as file:
        file.write(all_text)
    
    return all_text

class TestFullWidthFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        input_pdf = config["source_filename"]
        extract_text(input_pdf)
    
    def test_check_full_width(self):
        full_width_chars = ['／', '％', '’', '（', '）']
        file_path = "output_file.txt"
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        full_width_summary = []
        results = check_full_width(file_content, full_width_summary)
        for char in results:
            self.assertIn(char, full_width_chars, f'Expected {char} to be in {full_width_chars}')

    def test_get_positions(self):
        full_width_chars = {'／', '％', '’', '（', '）'}
        file_path = "output_file.txt"
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Create mock objects for page and page_highlights
        page = MagicMock()
        page_highlights = {}

        # Set the expected behavior for the search_for method of the page object
        def search_for_side_effect(x):
            if x in full_width_chars:
                return [fitz.Rect(10, 20, 30, 40)]
            else:
                return []
        
        page.search_for.side_effect = search_for_side_effect

        get_positions(full_width_chars, text, page, page_highlights)

        # Check if page_highlights is updated as expected
        for char in full_width_chars:
            self.assertIn(char, page_highlights)
            self.assertEqual(len(page_highlights[char]), 1)
            self.assertTrue(rects_are_equal(page_highlights[char][0], fitz.Rect(10, 20, 30, 40)))

if __name__ == '__main__':
    unittest.main()