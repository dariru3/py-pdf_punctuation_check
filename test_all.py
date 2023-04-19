import unittest
from unittest.mock import MagicMock
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
        cls.full_width_chars = {'／', '％', '’', '（', '）'}
        cls.output_file = "output_file.txt"
        input_pdf = config["source_filename"]
        extract_text(input_pdf)

        def search_for_side_effect(x, max_matches=None):
            if x in cls.full_width_chars:
                return [fitz.Rect(10, 20, 30, 40)]
            else:
                return []
            
        cls.search_for_side_effect = search_for_side_effect
    
    def test_check_full_width(self):
        with open(self.output_file, 'r', encoding='utf-8') as file:
            file_content = file.read()

        full_width_summary = []
        results = check_full_width(file_content, full_width_summary)
        for char in results:
            self.assertIn(char, self.full_width_chars, f'Expected {char} to be in {self.full_width_chars}')

    def test_get_positions(self):
        with open(self.output_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Create mock objects for page and page_highlights
        page = MagicMock()
        page_highlights = {}

        # Set the expected behavior for the search_for method of the page object    
        page.search_for.side_effect = self.search_for_side_effect

        get_positions(self.full_width_chars, text, page, page_highlights)

        # Check if page_highlights is updated as expected
        for char in self.full_width_chars:
            self.assertIn(char, page_highlights)
            self.assertEqual(len(page_highlights[char]), 1)
            self.assertTrue(rects_are_equal(page_highlights[char][0], fitz.Rect(10, 20, 30, 40)))

    def test_add_highlight_annot(self):
        with open(self.output_file, 'r', encoding='utf-8') as file:
            text = file.read()

        page = MagicMock()
        page_highlights = {}

        # Set the expected behavior for the search_for method of the page object
        page.search_for.side_effect = self.search_for_side_effect

        get_positions(self.full_width_chars, text, page, page_highlights)

        # Create mock objects for annot and info
        annot = MagicMock()
        info = {"title": "", "content": ""}

        # Set the expected behavior for the page and annot objects
        page.add_highlight_annot.return_value = annot
        annot.info = info

        comment_name = "Sample Comment"

        for char, match_rects in page_highlights.items():
            for rect in match_rects:
                add_highlight_annot({char: [rect]}, page, comment_name)

        # Verify if the add_highlight_annot method of the page object was called with the correct argument
        self.assertEqual(page.add_highlight_annot.call_count, len(self.full_width_chars))

        # Verify if the set_info and update methods of the annot object were called once
        annot.set_info.assert_called()
        annot.update.assert_called()

        # Verify if the info dictionary was updated as expected
        for char, match_rects in page_highlights.items():
            for rect in match_rects:
                self.assertEqual(info['title'], comment_name)
                self.assertEqual(info['content'], f"Replace {char} with half-width version")


if __name__ == '__main__':
    unittest.main()