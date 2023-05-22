import csv
import fitz
import unicodedata, re
from config import config

def highlight_punctuation_errors(input_file:str, pages:list=None):
    comment_name = "Punctuation Error Highlighter"
    # create matches list for output summary
    error_summary = []
    # open pdf
    pdfIn = fitz.open(input_file)
    # Iterate throughout pdf pages
    for pg, page in enumerate(pdfIn):
        pageID = pg+1
        # If required to look in specific pages
        if pages and pageID not in pages:
              continue

        # Get all the text in the page
        text = page.get_text("text")
        target_chars = check_punctuation_errors(text, error_summary)

        page_highlights = {}  # Initialize a dictionary to store match rectangles for each character
        get_positions(target_chars, text, page, page_highlights)
        add_highlight_annot(page_highlights, page, comment_name)

    export_summary(error_summary)
    save_output_file(input_file, pdfIn)

def check_full_width_chars(text, summary):
    full_width_chars = set()
    full_status = ['W', 'F', 'A']
    full_width_pattern = re.compile("[\uFF01-\uFF5E]+")

    excluded_chars = {
        '\u0022',  # Half-width double quote mark (")
        '\u0027',  # Half-width single quote mark/apostrophe (')
        '\u2018',  # Left single quotation mark (‘)
        '\u2019',  # Right single quotation mark (’)
        '\u201C',  # Left double quotation mark (“)
        '\u201D',  # Right double quotation mark (”)
        '\u2014',  # Em dash (—)
    }

    status_descriptions = {
        'W': 'Full-width: Wide',
        'F': 'Full-width: Full-width',
        'A': 'Full-width: Ambiguous'
    }

    for char in text:
        if char not in excluded_chars:
            status = unicodedata.east_asian_width(char)
            if status in full_status or full_width_pattern.search(char):
                description = status_descriptions.get(status, 'Unknown status')
                full_width_chars.add((char, description))
                update_summary(summary, char, description)

    return full_width_chars

def check_punctuation_patterns(text, summary):
    punctuation_errors = set()
    pattern = re.compile(
        # r"(?P<double_space>(?<=\S)[.,;:!?]\s{2}(?=\S))|"  # Double space after punctuation [removed for false-positives]
        r"(?P<straight_quotes>['\"])|"  # Straight quotes
        r"(?P<space_around_punct>\s[.,;:?!'\[\]{}()“”‘’%$¥—-]\s)|"  # Space before and after punctuation
        r"(?P<space_before_closing_quote>\s[’”](?=[a-zA-Z0-9]))|"  # Space before closing quotation mark followed by a character
        r"(?P<repeated_punct>(?:(?P<punct>[.,;:?!'\[\]{}()“”‘’&%$¥—-]))(?P=punct))|"  # Same punctuation is used twice in a row
        r"(?P<no_closing_parenthesis>\([^)]*$)" # Match a parethesis not closed
    )

    for match in pattern.finditer(text):
        error_type = match.lastgroup
        error_char = match.group()
        error_description = {
            'double_space': 'Double space after punctuation',
            'straight_quotes': 'Straight quotes',
            'space_around_punct': 'Space before and after punctuation',
            'space_before_closing_quote': 'Space before closing quotation mark followed by a character',
            'repeated_punct': 'Same punctuation is used twice in a row',
            'no_closing_parenthesis': 'Missing closing parenthesis'
        }.get(error_type, 'Unknown error')

        punctuation_errors.add((error_char, error_description))
        update_summary(summary, error_char, error_description)

    return punctuation_errors

def check_punctuation_errors(text, summary):
    errors = check_full_width_chars(text, summary) | check_punctuation_patterns(text, summary)
    error_characters = []
    for error_char, error_description in errors:
        error_characters.append([error_char, error_description])

    return error_characters

def update_summary(summary:list, char, description):
    found = False
    for entry in summary:
        if entry['char'] == char:
            entry['count'] += 1
            found = True
            break
    if not found:
        summary.append({'char': char, 'count': 1, 'description': description})

def get_positions(target_chars, text, page, page_highlights):
    for char, description in target_chars:
        start_idx = 0
        while True:
            start_idx = text.find(char, start_idx)
            if start_idx == -1:
                break
            end_idx = start_idx + len(char)
            matches = page.search_for(text[start_idx:end_idx])
            if matches:
                handle_matches(matches, char, description, page_highlights)
            start_idx += 1

def handle_matches(matches, char, description, page_highlights):
    for match in matches:
        if char not in page_highlights:
            page_highlights[char] = {"matches": [match], "description": description}
        else:
            # Check if the match rectangle is not already in the list
            if not any([rects_are_equal(match, rect, threshold=1) for rect in page_highlights[char]["matches"]]):
                page_highlights[char]["matches"].append(match)

def rects_are_equal(rect1, rect2, threshold=1e-6):
    return all([abs(rect1[i] - rect2[i]) < threshold for i in range(4)])

def add_highlight_annot(page_highlights:dict, page, comment_name):
    # print(f"Page highlights: {page_highlights}")
    for char, char_data in page_highlights.items():
        match_rects = char_data["matches"]
        description = char_data["description"]
        for rect in match_rects:
            annot = page.add_highlight_annot(rect)
            info = annot.info
            info["title"] = comment_name
            info["content"] = f"Error found: {char} ({description})"
            annot.set_info(info)
            annot.update()

def export_summary(error_summary:list):
    fieldnames = ['Character', 'Count', 'Description']
    with open("error_summary.csv", mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in error_summary:
            csv_writer.writerow({
                fieldnames[0]: entry['char'],
                fieldnames[1]: entry['count'],
                fieldnames[2]: entry['description']
            })

def save_output_file(input_file, pdfIn):
    output_file = input_file.split(".")[0] + " punctuation_errors.pdf"
    pdfIn.save(output_file, garbage=3, deflate=True)
    pdfIn.close()

if __name__ == '__main__':
    highlight_punctuation_errors(input_file=config["source_filename"])