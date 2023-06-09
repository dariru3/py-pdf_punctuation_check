# Punctuation Error Highlighter

This Python program detects and highlights punctuation errors in PDF files. It also generates an error summary in CSV format. It detects the following errors:
- Full-width characters
- Straight quotes
- Spaces around punctuation
- Space before closing quotation marks followed by a character
- Repeated punctuation
- Missing closing parenthesis, brackets, braces, and double quotation marks
- ¥ and yen used at the same time
- Incorrect apostrophe for year abbreviation
- Apostrophe in a decade

Additionally, it allows you to skip certain characters and provides the option to ignore Japanese characters.

## Dependencies

- Python 3.7 or later
- PyMuPDF (fitz) module
- regex module
- unicodedata module

## How to use

1. Install the required dependencies:

```bash
pip install PyMuPDF regex
```

2. Configure the `config.py` file with the desired settings:

```python
config = {
    "source_filename": "path/to/your/input_file.pdf",
}
```

3. Run the program:

```bash
python main.py
```

The program will process the input PDF file and generate an output PDF file with highlighted errors (`input_file_punctuation_errors.pdf`). It will also create a CSV file (`error_summary.csv`) containing a summary of the detected errors.

## Main functions

- `highlight_punctuation_errors(input_file:str, pages:list=None, skip_chars:str="",skip_japanese:bool=False)`: The main function that processes the input PDF file and highlights the punctuation errors. You can specify pages to check, characters to skip, and whether to skip Japanese characters.

- `check_full_width_chars(text, skip_chars, skip_japanese)`: Checks for full-width characters in the input text.

- `check_excluded_chars(skip_chars:set, skip_japanese:bool=False)`: Determines the characters to be excluded from the check.

- `check_punctuation_patterns(text)`: Checks for other punctuation errors in the input text using regex patterns.

- `check_incomplete_pairs(text)`: Checks for incomplete pairs of punctuation.

- `check_punctuation_errors(text, summary, skip_chars="", skip_japanese=False)`: Combines the results of `check_full_width_chars`, `check_punctuation_patterns` and `check_incomplete_pairs`.

- `update_summary(summary:list, char, description, count=1)`: Updates the error summary with new characters or increments the count of existing characters.

- `add_highlight_annot(page_highlights:dict, page, comment_name, error_summary:list)`: Adds highlight annotations to the PDF page based on the `page_highlights` dictionary and updates the error summary.

### Helper functions
- `get_positions(target_chars, text, page, page_highlights)`: Gets the positions of the target characters in the text and populates the `page_highlights` dictionary.

- `handle_matches(matches, char, description, page_highlights)`: Adds the match rectangles to the `page_highlights` dictionary.

- `rects_are_equal(rect1, rect2, threshold=1e-6)`: Compares two rectangles for equality with a given threshold.

- `rect_is_valid(rect)`: Checks if a rectangle is valid (x1 < x2 and y1 < y2).

- `export_summary(error_summary:list)`: Exports the error summary to a CSV file.

- `save_output_file(input_file, pdfIn)`: Saves the processed PDF file with highlighted errors.

## Resources
PyMuPDF documentation (classes): [link](https://pymupdf.readthedocs.io/en/latest/classes.html)

Checking a character is fullwidth or halfwidth in Python: [link 1](https://stackoverflow.com/questions/23058564/checking-a-character-is-fullwidth-or-halfwidth-in-python), [link 2](http://www.unicode.org/reports/tr44/tr44-4.html#Validation_of_Enumerated)

Google Colab (virtual Python environment): [link](https://colab.research.google.com/)

## Contributions
Contributions are welcome. If you find a bug or have suggestions for improvements, please open an issue or a pull request.