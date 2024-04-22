import csv
import fitz
import unicodedata, re
import os
import nltk
from nltk.corpus import words
# nltk.download('words')

def highlight_punctuation_errors(input_file:str, output_filename_end:str, summary_filename:str, pages:list=None, skip_chars:str="", skip_japanese:bool=False, skip_hyphens:bool=False):
    comment_name = "PunctChecker"
    skip_chars = set(skip_chars) if skip_chars else set()
    error_summary = []

    input_pdf = fitz.open(input_file)
    for page_num, page in enumerate(input_pdf):
        page_num +=1
        if pages and page_num not in pages:
              continue

        text = page.get_text("text")
        target_chars = check_punctuation_errors(text, error_summary, skip_chars, skip_japanese, skip_hyphens)

        highlight_errors(target_chars, text, page, comment_name, error_summary)

    # export_summary(error_summary, summary_filename)
    save_output_file(input_file, input_pdf, output_filename_end)

def check_hyphenation_errors(text):
    hyphenation_errors = set()
    word_list = set(words.words())  # Set of valid English words from NLTK
    hyphenated_words = re.findall(r'\b[a-zA-Z]+-[a-zA-Z]+\b', text)  # Finds hyphenated words

    for word in hyphenated_words:
        parts = word.split('-')
        # Check if both parts of the hyphenated word are valid words
        if any(part.lower() not in word_list for part in parts):
            hyphenation_errors.add((word, '不適切なハイフネーション'))

    return hyphenation_errors

def check_full_width_chars(text, skip_chars, skip_japanese):
    full_width_chars = set()
    full_status = ['W', 'F', 'A']
    full_width_pattern = re.compile("[\uFF01-\uFF5E]+")

    excluded_chars = check_excluded_chars(skip_chars, skip_japanese)

    status_descriptions = {
        'W': '全角を半角に', # Full-width: Wide
        'F': '半角に', # Full-width: Full-width
        'A': '半角か確認' # Full-width: Ambiguous
    }

    for char in text:
        if char not in excluded_chars:
            status = unicodedata.east_asian_width(char)
            if status in full_status or full_width_pattern.search(char):
                description = status_descriptions.get(status, 'エラー不明')
                full_width_chars.add((char, description))

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
    punctuation_errors = set()
    error_patterns = re.compile(
        r"(?P<straight_quotes>['\"])|"  # Straight quotes
        r"(?P<space_around_punct>\s[.,;:?!'\[\]{}()“”‘’%$¥—-]\s)|"  # Space before and after punctuation
        r"(?P<space_before_closing_quote>\s[’”](?=[a-zA-Z0-9]))|"  # Space before closing quotation mark followed by a character
        r"(?P<repeated_punct>(?:(?P<punct>[.,;:?!'\[\]{}()“”‘’&%$¥—-]))(?P=punct))|"  # Same punctuation is used twice in a row
        r"(?P<yen_symbol_and_word>¥[\w.,]+\syen)|" # ¥ and yen used at the same time
        r"(?P<incorrect_year_abbr>‘\d{2})|"  # Incorrect year abbreviation
        r"(?P<apostrophe_in_decade>\b\d{2,4}'s\b)|"  # Apostrophe in decade
        r"(?P<missing_space_after_sent>[a-zA-Z]([.?!])[a-zA-Z])"  # No space after punctuation between letters
    )
    
    error_descriptions = {
        'straight_quotes': 'オタマジャクシ型に',
        'space_around_punct': '記号の前後のスペースを詰める',
        'space_before_closing_quote': '開始のクォーテーションマークに変更',
        'repeated_punct': 'マーク重複',
        'yen_symbol_and_word': '¥ かyen か選択',
        'incorrect_year_abbr': 'シングルクォーテーションの向きが逆',
        'apostrophe_in_decade': 'クォーテーション不要',
        'missing_space_after_sent': '文章間の句読点の後にスペースがない'
    }

    for error_match in error_patterns.finditer(text):
        error_type = error_match.lastgroup
        error_char = error_match.group()
        description = error_descriptions.get(error_type, 'エラー不明')

        punctuation_errors.add((error_char, description))
    return punctuation_errors

def check_incomplete_pairs(text):
    punctuation_pairs = {
        '(': ')',
        '[': ']',
        '{': '}',
        '“': '”'
    }

    reverse_punctuation_pairs = {value: key for key, value in punctuation_pairs.items()}

    stack = []
    errors = set()
    max_string_length = 4  # Maximum characters to return including the punctuation

    for i, char in enumerate(text):
        if char in punctuation_pairs:
            stack.append((char, i))
        elif char in reverse_punctuation_pairs:
            if stack:
                start_punct, _ = stack[-1]
                if start_punct == reverse_punctuation_pairs[char]:
                    stack.pop()
                    continue
            # Extract the string after the punctuation, up to max_string_length characters
            end_pos = min(i+1+max_string_length, len(text))
            errors.add((text[i: end_pos], '対応するマークがない。要確認'))
        else:
            continue

    while stack:
        start_punct, pos = stack.pop()
        # Extract the string after the punctuation, up to max_string_length characters
        end_pos = min(pos+max_string_length, len(text))
        errors.add((text[pos: end_pos], '対応するマークがない。要確認'))
    
    return errors

def check_punctuation_errors(text, summary, skip_chars, skip_japanese=False, skip_hyphens=False):
    errors = (
        check_full_width_chars(text, skip_chars, skip_japanese) 
        | check_punctuation_patterns(text) 
        | check_incomplete_pairs(text)
    )
    if not skip_hyphens:
        errors |= check_hyphenation_errors(text)
    error_characters = []
    for error_char, error_description in errors:
        error_characters.append([error_char, error_description])
        update_summary(summary, error_char, error_description)
    return error_characters

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
            # print(char, description, match, len(page_highlights[char]))
            if not any([rects_are_equal(match, rect, threshold=1) for rect in page_highlights[char]["matches"]]):
                page_highlights[char]["matches"].append(match)

def rects_are_equal(rect1, rect2, threshold=1e-6):
    return all([abs(rect1[i] - rect2[i]) < threshold for i in range(4)])

def add_highlights(page_highlights:dict, page, comment_name, error_summary:list):
    for char, char_data in page_highlights.items():
        match_rects = char_data["matches"]
        description = char_data["description"]
        for rect in match_rects:
            if not rect_is_valid(rect):
                update_summary(error_summary, char, f"{description}, error on page {page.number+1} NOT highlighted!", count=1)
                continue
            annot = page.add_highlight_annot(rect)
            info = annot.info
            info["title"] = comment_name
            info["content"] = f"「{char}」{description}" # PDF comment template
            annot.set_info(info)
            annot.update()

def rect_is_valid(rect):
    #Check if a rectangle is valid (x1 < x2 and y1 < y2).
    x1, y1, x2, y2 = rect
    return x1 < x2 and y1 < y2

def highlight_errors(target_char, text, page, comment_name, error_summary):
    page_highlights = {}
    get_positions(target_char, text, page, page_highlights)
    add_highlights(page_highlights, page, comment_name, error_summary)

def export_summary(error_summary:list, summary_filename):
    fieldnames = ['Character', 'Count', 'Description']
    with open(f"input_files/{summary_filename}.csv", mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in error_summary:
            csv_writer.writerow({
                fieldnames[0]: entry['char'],
                fieldnames[1]: entry['count'],
                fieldnames[2]: entry['description']
            })

def save_output_file(input_file, input_pdf, output_filename_end):
    output_file_name = input_file.split(".")[0] + f" {output_filename_end}.pdf"
    input_pdf.save(output_file_name, garbage=3, deflate=True)
    input_pdf.close()

def process_directory(dir_name:str, output_filename_end:str, pages:list=None, skip_chars:str="", skip_japanese:bool=False, skip_hyphens:bool=False):
    processed_files = set()
    for file_name in os.listdir(dir_name):
        if file_name.endswith(output_filename_end + ".pdf"):
            processed_files.add(file_name)
            source_file_name = file_name.replace(f" {output_filename_end}.pdf", ".pdf")
            processed_files.add(source_file_name)
        
    for file_name in os.listdir(dir_name):
        if file_name.endswith(".pdf") and file_name not in processed_files:
            full_path = os.path.join(dir_name, file_name)
            summary_filename = file_name[:-4] + " error_summary"
            highlight_punctuation_errors(full_path, output_filename_end, summary_filename, pages, skip_chars, skip_japanese, skip_hyphens)
        else:
            print(f'Skipping {file_name}')

if __name__ == '__main__':
    dir_name = "/Users/daryl-villalobos/Google Drive/My Drive/Punct Checker Magic Box"
    output_filename_end = "punct_checker"
    process_directory(dir_name, output_filename_end, skip_chars="•", skip_japanese=True, skip_hyphens=False)
