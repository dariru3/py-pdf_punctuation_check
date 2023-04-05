import csv
import fitz
import unicodedata, re
import config

def highlight_full_width(input_file:str, pages:list=None):
    comment_name = "Full-Width Highlighter"
    # create matches list for output summary
    full_width_summary = []
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
        full_width_chars = check_full_width(text, full_width_summary)

        page_highlights = {}  # Initialize a dictionary to store match rectangles for each character
        get_positions(full_width_chars, text, page, page_highlights)
        add_highlight_annot(page_highlights, page, comment_name)

    export_summary(full_width_summary)
    save_output_file(input_file, pdfIn)

def check_full_width(text, full_width_summary):
    temp_set = set()
    full_status = ['W', 'F', 'A']
    pattern = re.compile("[\uFF01-\uFF5E]+")

    excluded_chars = {
        '\u0022',  # Half-width double quote mark (")
        '\u0027',  # Half-width single quote mark/apostrophe (')
        '\u2018',  # Left single quotation mark (‘)
        '\u2019',  # Right single quotation mark (’)
        '\u201C',  # Left double quotation mark (“)
        '\u201D',  # Right double quotation mark (”)
        '\u2014',  # Em dash (—)
    }

    for char in text:
        if char not in excluded_chars:
            status = unicodedata.east_asian_width(char)
            if status in full_status and pattern.search(char) is None:
                temp_set.add(char)
                update_summary(full_width_summary, char, status)
    return temp_set

def update_summary(full_width_summary:list, char, status):
    found = False
    for entry in full_width_summary:
        if entry['char'] == char:
            entry['count'] += 1
            found = True
            break
    if not found:
        full_width_summary.append({'char': char, 'count': 1, 'type': status})

def get_positions(full_width_chars, text, page, page_highlights):
    for char in full_width_chars:
        start_idx = 0
        while True:
            start_idx = text.find(char, start_idx)
            if start_idx == -1:
                break
            end_idx = start_idx + len(char)
            matches = page.search_for(text[start_idx:end_idx])
            if matches:
                handle_matches(matches, char, page_highlights)
            start_idx += 1

def handle_matches(matches, char, page_highlights):
    for match in matches:
        if char not in page_highlights:
            page_highlights[char] = [match]
        else:
            # Check if the match rectangle is not already in the list
            if not any([rects_are_equal(match, rect) for rect in page_highlights[char]]):
                page_highlights[char].append(match)

def rects_are_equal(rect1, rect2):
    return all([abs(rect1[i] - rect2[i]) < 1e-6 for i in range(4)])

def add_highlight_annot(page_highlights:dict, page, comment_name):
    for char, match_rects in page_highlights.items():
        for rect in match_rects:
            annot = page.add_highlight_annot(rect)
            info = annot.info
            info["title"] = comment_name
            info["content"] = f"Replace {char} with half-width version"
            annot.set_info(info)
            annot.update()

def export_summary(full_width_summary:list):
    fieldnames = ['Character', 'Count', 'Type']
    with open("full-width_summary.csv", mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in full_width_summary:
            csv_writer.writerow({
                fieldnames[0]: entry['char'],
                fieldnames[1]: entry['count'],
                fieldnames[2]: entry['type']
            })

def save_output_file(input_file, pdfIn):
    output_file = input_file.split(".")[0] + " full-width_highlight.pdf"
    pdfIn.save(output_file, garbage=3, deflate=True)
    pdfIn.close()

highlight_full_width(input_file=config.config["source_filename"])