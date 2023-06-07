# Punctuation Error Highlighter

This Python program detects and highlights punctuation errors in PDF files. It also generates an error summary in CSV format. It detects the following errors:
- Full-width characters
- ~Double spaces after punctuation~
- Straight quotes
- Spaces around punctuation
- Space before closing quotation marks followed by a character
- Repeated punctuation
- Missing closing parenthesis

## Dependencies

- Python 3.7 or later
- PyMuPDF (fitz) module
- regex module

## How to use

1. Install the required dependencies:

```bash
pip install PyMuPDF
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

## Functions

- `highlight_punctuation_errors(input_file:str, pages:list=None)`: The main function that processes the input PDF file and highlights the punctuation errors.

- `check_full_width_chars(text, summary)`: Checks for full-width characters in the input text.

- `check_punctuation_patterns(text, summary)`: Checks for other punctuation errors in the input text using regex patterns.

- `check_punctuation_errors(text, summary)`: Combines the results of `check_full_width_chars` and `check_punctuation_patterns`.

- `update_summary(summary:list, char, description)`: Updates the error summary with new characters or increments the count of existing characters.

- `get_positions(target_chars, text, page, page_highlights)`: Gets the positions of the target characters in the text and populates the `page_highlights` dictionary.

- `handle_matches(matches, char, description, page_highlights)`: Adds the match rectangles to the `page_highlights` dictionary.

- `rects_are_equal(rect1, rect2)`: Compares two rectangles for equality.

- `add_highlight_annot(page_highlights:dict, page, comment_name)`: Adds highlight annotations to the PDF page based on the `page_highlights` dictionary.

- `export_summary(error_summary:list)`: Exports the error summary to a CSV file.

- `save_output_file(input_file, pdfIn)`: Saves the processed PDF file with highlighted errors.

## Resources
Installing Python packages for VS Code on MacOS: [link](https://www.mytecbits.com/internet/python/installing-python-packages)

PyMuPDF documentation (classes): [link](https://pymupdf.readthedocs.io/en/latest/classes.html)

Checking a character is fullwidth or halfwidth in Python: [link 1](https://stackoverflow.com/questions/23058564/checking-a-character-is-fullwidth-or-halfwidth-in-python), [link 2](http://www.unicode.org/reports/tr44/tr44-4.html#Validation_of_Enumerated)

Google Colab (virtual Python environment): [link](https://colab.research.google.com/)
