import unittest
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
    def test_extract_text(self):
        input_pdf = config["source_filename"]

        extract_text(input_pdf)
        output_text_file = 'output_file.txt'

        self.assertTrue(os.path.exists(output_text_file))
    
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