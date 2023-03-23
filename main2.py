import fitz, unicodedata
import config

def rects_are_equal(rect1, rect2):
    return all([abs(rect1[i] - rect2[i]) < 1e-6 for i in range(4)])

def check_full_width(input_file:str, pages:list=None):
    comment_name = "Full-Width Highlighter"
    comment = "Found"
    # create matches dictionary for output summary
    full_width_matches = {}
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
                if char in full_width_matches:
                    full_width_matches[char][0] += 1
                else:
                    full_width_matches[char] = [1, status]

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

    print(full_width_matches)

    # Save to output file
    output_file = input_file.split(".")[0] + " comments.pdf"
    pdfIn.save(output_file, garbage=3, deflate=True)
    pdfIn.close()

check_full_width(input_file=config.config["source_filename"])