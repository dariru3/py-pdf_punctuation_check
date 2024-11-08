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
- Improper hyphenation

Additionally, it allows you to skip certain characters and provides the option to ignore Japanese characters.

## Dependencies

- Python 3.7 or later
- PyMuPDF (fitz) module
- Regex module
- Unicodedata module
- NLTK module with the `words` corpus

## How to use

1. Install the required dependencies:

```bash
pip install pymupdf regex nltk
```

Download the `words` corpus for NLTK:

```python
import nltk
nltk.download('words')
```

2. Configure the directory and other settings directly in the `main.py` file as needed.

3. Run the program:

```bash
python main.py
```

The program processes all PDF files in the `input_files` directory, highlighting punctuation errors in each and generating an output file with an appended name (`input_file_punct_checker.pdf`). It also creates a CSV file (`error_summary.csv`) containing a summary of the detected errors.

## Main functions

- `highlight_punctuation_errors(input_file:str, output_filename_end:str, summary_filename:str, pages:list=None, skip_chars:str="", skip_japanese:bool=False, skip_hyphens:bool=False)`: Processes the input PDF file and highlights the punctuation errors.

- `check_full_width_chars(text, skip_chars, skip_japanese)`: Checks for full-width characters in the input text.

- `check_hyphenation_errors(text)`: Checks for improper hyphenation in the input text by comparing with known English words.

- `check_excluded_chars(skip_chars:set, skip_japanese:bool=False)`: Determines the characters to be excluded from the check.

- `check_punctuation_patterns(text)`: Checks for other punctuation errors using regex patterns.

- `check_incomplete_pairs(text)`: Checks for incomplete pairs of punctuation.

- `export_summary(error_summary:list, summary_filename)`: Exports the error summary to a CSV file.

- `save_output_file(input_file, input_pdf, output_filename_end)`: Saves the processed PDF file with highlighted errors.

- `process_directory(dir_name:str, output_filename_end:str, pages:list=None, skip_chars:str="", skip_japanese:bool=False, skip_hyphens:bool=False)`: Processes multiple PDF files in a directory, skipping already processed files.

### Helper functions

- `get_positions(target_chars, text, page, page_highlights)`: Gets the positions of the target characters in the text and populates the `page_highlights` dictionary.

- `handle_matches(matches, char, description, page_highlights)`: Adds the match rectangles to the `page_highlights` dictionary.

- `rects_are_equal(rect1, rect2, threshold=1e-6)`: Compares two rectangles for equality.

- `rect_is_valid(rect)`: Checks if a rectangle is valid.

## Resources

- PyMuPDF documentation (classes): [link](https://pymupdf.readthedocs.io/en/latest/classes.html)
- Checking a character is fullwidth or halfwidth in Python: [link 1](https://stackoverflow.com/questions/23058564/checking-a-character-is-fullwidth-or-halfwidth-in-python), [link 2](http://www.unicode.org/reports/tr44/tr44-4.html#Validation_of_Enumerated)
- Google Colab (virtual Python environment): [link](https://colab.research.google.com/)

## Contributions

Contributions are welcome. If you find a bug or have suggestions for improvements, please open an issue or a pull request.
