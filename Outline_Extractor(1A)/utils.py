import pdfplumber
import re
from collections import defaultdict, Counter

def normalize_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def detect_heading_level(text):
    if re.match(r'^\d+\.\d+\.\d+', text):
        return "H3"
    elif re.match(r'^\d+\.\d+', text):
        return "H2"
    elif re.match(r'^\d+', text):
        return "H1"
    return None

def is_valid_heading(text):
    # Filters out long sentences, bullets, tables, URLs
    if len(text) > 80: return False
    if re.search(r'https?://|www\.|\.com', text, re.IGNORECASE): return False
    if re.match(r'^[\-\•]+$', text.strip()): return False
    if len(text.split()) > 10: return False
    if text.strip().isdigit(): return False
    return True

def extract_outline(pdf_path):
    lines_by_font = []
    all_sizes = []
    bold_lines_page_0 = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            lines = defaultdict(list)

            for word in words:
                y = round(word['top'], 1)
                size = round(word['size'], 1)
                fontname = word.get("fontname", "").lower()

                lines[(y, size)].append(word)
                all_sizes.append(size)

            for (y, size), words_in_line in lines.items():
                line_text = normalize_text(" ".join(w['text'] for w in sorted(words_in_line, key=lambda w: w['x0'])))
                fontnames = [w.get("fontname", "").lower() for w in words_in_line]
                dominant_font = max(set(fontnames), key=fontnames.count)

                if page_num == 0 and "bold" in dominant_font and size >= 12:
                    bold_lines_page_0.append((y, size, line_text, dominant_font))

                if line_text:
                    lines_by_font.append((line_text, size, page_num, dominant_font))

    if not lines_by_font:
        return {"title": "", "outline": []}

    size_freq = Counter([size for _, size, _, _ in lines_by_font])
    body_size = size_freq.most_common(1)[0][0]

    # ---------- TITLE DETECTION ----------
    title = ""
    if bold_lines_page_0:
        bold_lines_page_0.sort()
        grouped = []
        current = [bold_lines_page_0[0]]
        for i in range(1, len(bold_lines_page_0)):
            y1 = bold_lines_page_0[i-1][0]
            y2 = bold_lines_page_0[i][0]
            if abs(y2 - y1) < 20:
                current.append(bold_lines_page_0[i])
            else:
                grouped.append(current)
                current = [bold_lines_page_0[i]]
        grouped.append(current)
        best_group = max(grouped, key=len)
        title = normalize_text(" ".join(item[2] for item in best_group))
    else:
        # fallback if needed
        title = lines_by_font[0][0]

    # ---------- OUTLINE DETECTION ----------
    outline = []
    seen = set()
    for text, size, page, font in lines_by_font:
        if text.lower() in seen or not is_valid_heading(text):
            continue
        if "bold" in font and size >= body_size + 2:
            seen.add(text.lower())
            outline.append({"level": "H1", "text": text, "page": page})

    # Remove title from outline
    outline = [item for item in outline if normalize_text(item['text']) != normalize_text(title)]

    return {"title": title.strip(), "outline": outline}
