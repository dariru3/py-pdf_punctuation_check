import csv
import fitz
import unicodedata
import config

def check_full_width(input_file:str, pages:list=None):
    comment_name = "Full-Width Highlighter"
    comment = "Found"
    # create matches list for output summary
    full_width_matches = []
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

        # Split the text by characters and check if each character is full-width
        full_width_chars = set()
        for char in text:
            status = unicodedata.east_asian_width(char)
            full_status = ['W', 'F', 'A']
            if status in full_status:
                full_width_chars.add(char)
                # Update summary
                found = False
                for entry in full_width_matches:
                    if entry['char'] == char:
                        entry['count'] += 1
                        found = True
                        break
                if not found:
                    full_width_matches.append({'char': char, 'count': 1, 'type': status})

        # Get the positions of full-width characters in the page
        page_highlights = {}  # Initialize a dictionary to store match rectangles for each character
        for char in full_width_chars:
            start_idx = 0
            while True:
                start_idx = text.find(char, start_idx)
                if start_idx == -1:
                    break
                end_idx = start_idx + len(char)
                matches = page.search_for(text[start_idx:end_idx])
                if matches:
                    for match in matches:
                        if char not in page_highlights:
                            page_highlights[char] = [match]
                        else:
                            # Check if the match rectangle is not already in the list
                            if not any([rects_are_equal(match, rect) for rect in page_highlights[char]]):
                                page_highlights[char].append(match)
                start_idx += 1

        # Add highlight annotations
        for char, match_rects in page_highlights.items():
            for rect in match_rects:
                annot = page.add_highlight_annot(rect)
                annot.update()

    # Write the results to a CSV file using DictWriter
    fieldnames = ['Character', 'Count', 'Type']
    with open("summary.csv", mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in full_width_matches:
            csv_writer.writerow({
                'Character': entry['char'],
                'Count': entry['count'],
                'Type': entry['type']
            })

    # Save to output file
    output_file = input_file.split(".")[0] + " comments.pdf"
    pdfIn.save(output_file, garbage=3, deflate=True)
    pdfIn.close()

def rects_are_equal(rect1, rect2):
    return all([abs(rect1[i] - rect2[i]) < 1e-6 for i in range(4)])

check_full_width(input_file=config.config["source_filename"])