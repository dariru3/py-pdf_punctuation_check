import csv
import fitz
import unicodedata, re
from config import config

def highlight_punctuation_errors(input_file:str, pages:list=None, skip_chars:str="",skip_japanese:bool=False):
    comment_name = "PunctChecker" # set PDF comment author
    skip_chars = set(skip_chars) if skip_chars else set() # convert skip_chars to a set for efficient membership testing
    error_summary = [] # create error matches list for output summary

    pdfIn = fitz.open(input_file) # open pdf
    # Iterate throughout pdf pages
    for pg, page in enumerate(pdfIn):
        pageID = pg+1
        if pages and pageID not in pages: # If required to look in specific pages
              continue

        text = page.get_text("text") # Get all the text in the page
        
        target_chars = check_punctuation_errors(text, error_summary, skip_chars, skip_japanese)

        page_highlights = {}  # Initialize a dictionary to store match rectangles for each character
        get_positions(target_chars, text, page, page_highlights)
        add_highlight_annot(page_highlights, page, comment_name,error_summary)

    export_summary(error_summary)
    save_output_file(input_file, pdfIn)

def check_full_width_chars(text, skip_chars, skip_japanese):
    full_width_chars = []
    full_status = ['W', 'F', 'A']
    full_width_pattern = re.compile("[\uFF01-\uFF5E]+")

    excluded_chars = check_excluded_chars(skip_chars, skip_japanese)

    status_descriptions = {
        'W': 'Full-width: Wide',
        'F': 'Full-width: Full-width',
        'A': 'Full-width: Ambiguous'
    }

    for match in full_width_pattern.finditer(text):
        matched_chars = match.group()
        for char_idx, char in enumerate(matched_chars):
            if char not in excluded_chars:
                status = unicodedata.east_asian_width(char)
                if status in full_status:
                    description = status_descriptions.get(status, 'Unknown status')
                    full_width_chars.append((char, description, match.start()+char_idx, match.start()+char_idx+1))

    return full_width_chars

def check_excluded_chars(skip_chars:set, skip_japanese:bool=False):

    excluded_chars = {
        '\u0022',  # Half-width double quote mark (")
        '\u0027',  # Half-width single quote mark/apostrophe (')
        '\u2018',  # Left single quotation mark (‘)
        '\u2019',  # Right single quotation mark (’)
        '\u201C',  # Left double quotation mark (“)
        '\u201D',  # Right double quotation mark (”)
        '\u2014',  # Em dash (—)
    }

    # add to excluded_chars, if necessary
    excluded_chars.update(skip_chars)
    if skip_japanese:
        excluded_chars.update(set(chr(i) for i in range(0x3040, 0x30A0)))  # Hiragana
        excluded_chars.update(set(chr(i) for i in range(0x30A0, 0x3100)))  # Katakana
        excluded_chars.update(set(chr(i) for i in range(0x4E00, 0x9FB0)))  # Kanji

    return excluded_chars

def check_punctuation_patterns(text):
    punctuation_errors = []
    error_patterns = re.compile(
        r"(?P<straight_quotes>['\"])|"  # Straight quotes
        r"(?P<space_around_punct>\s[.,;:?!'\[\]{}()“”‘’%$¥—-]\s)|"  # Space before and after punctuation
        r"(?P<space_before_closing_quote>\s[’”](?=[a-zA-Z0-9]))|"  # Space before closing quotation mark followed by a character
        r"(?P<repeated_punct>(?:(?P<punct>[.,;:?!'\[\]{}()“”‘’&%$¥—-]))(?P=punct))|"  # Same punctuation is used twice in a row
        r"(?P<yen_symbol_and_word>¥[\w.,]+\syen)|" # ¥ and yen used at the same time
        r"(?P<incorrect_year_abbr>‘\d{2})|"  # Incorrect year abbreviation
        r"(?P<apostrophe_in_decade>\b\d{2,4}'s\b)"  # Apostrophe in decade
    )
    
    error_descriptions = {
        'straight_quotes': 'Straight quotes',
        'space_around_punct': 'Space before and after punctuation',
        'space_before_closing_quote': 'Space before closing quotation mark followed by a character',
        'repeated_punct': 'Same punctuation is used twice in a row',
        'yen_symbol_and_word': '¥ and yen used at the same time',
        'incorrect_year_abbr': 'Incorrect apostrophe for year abbreviation',
        'apostrophe_in_decade': 'Apostrophe in decade'
    }

    for error_match in error_patterns.finditer(text):
        error_type = error_match.lastgroup
        error_char = error_match.group()
        description = error_descriptions.get(error_type, 'Unknown error')

        punctuation_errors.append((error_char, description, error_match.start(), error_match.end()))

    return punctuation_errors

def check_incomplete_pairs(text):
    # Define punctuation pairs
    punctuation_pairs = {
        '(': ')',
        '[': ']',
        '{': '}',
        '“': '”',
        # '‘': '’', # gets thrown off by apostrophes
    }

    errors = set()

    # Check for each pair
    for start_punct, end_punct in punctuation_pairs.items():
        if text.count(start_punct) != text.count(end_punct):
            errors.add((start_punct, 'Mismatched pair'))

    return errors

def check_punctuation_errors(text, summary, skip_chars="", skip_japanese=False):
    errors = check_punctuation_patterns(text)
    errors += check_full_width_chars(text, skip_chars, skip_japanese)
    for error_match, error_description, start, end in errors:
        error_char = error_match
        update_summary(summary, error_char, error_description)
    return errors

def update_summary(summary:list, char, description, count=1):
    found = False
    for entry in summary:
        if entry['char'] == char and entry['description'] == description:
            entry['count'] += count
            found = True
            break
    if not found:
        summary.append({'char': char, 'count': count, 'description': description})

def get_positions(target_chars, text, page, page_highlights):
    for char, description, start, end in target_chars:
        matches = page.search_for(text[start:end])
        if matches:
            handle_matches(matches, char, description, page_highlights)

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

def rect_is_valid(rect):
    #Check if a rectangle is valid (x1 < x2 and y1 < y2).
    x1, y1, x2, y2 = rect
    return x1 < x2 and y1 < y2

def add_highlight_annot(page_highlights:dict, page, comment_name, error_summary:list):
    for char, char_data in page_highlights.items():
        match_rects = char_data["matches"]
        description = char_data["description"]
        for rect in match_rects:
            # print("Rect:", rect)
            if not rect_is_valid(rect):
                # print(f"Invalid rect for {char} ({description}) on {page.number+1}")
                update_summary(error_summary, char, f"{description}, Invalid rect on page {page.number+1}! NOT highlighted!", count=1)
                continue
            annot = page.add_highlight_annot(rect)
            info = annot.info
            info["title"] = comment_name
            info["content"] = f"Error found: {char} ({description})"
            annot.set_info(info)
            annot.update()

def export_summary(error_summary:list):
    fieldnames = ['Character', 'Count', 'Description']
    with open("test_files/error_summary.csv", mode='w', newline='', encoding='utf-8') as csv_file:
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
    highlight_punctuation_errors(input_file=config["source_filename"], skip_chars="•", skip_japanese=True)