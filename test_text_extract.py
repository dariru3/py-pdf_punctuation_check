import fitz
from config import config as c

def highlight_full_width(input_file:str):
    pdfIn = fitz.open(input_file)

    all_text = ""

    for page in pdfIn:
        text = page.get_text("text")
        all_text += text
    
    with open("output_file.txt", 'w') as file:
        file.write(all_text)

if __name__ == '__main__':
    highlight_full_width(c["source_filename"])