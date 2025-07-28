import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_title_with_ocr(doc):
    """
    OCR fallback to extract title from the first page when text extraction fails
    """
    try:
        # Get the first page
        page = doc.load_page(0)
        
        # Render page as image
        mat = fitz.Matrix(2.0, 2.0)  # Increase resolution for better OCR
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(img_data))
        
        # Use OCR to extract text
        ocr_text = pytesseract.image_to_string(image)
        
        # Extract the first few lines as potential title
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        if lines:
            # Take the first 3 non-empty lines as potential title
            title_candidate = " ".join(lines[:3])
            # Clean up and return if reasonable length
            if 10 <= len(title_candidate) <= 200:
                return title_candidate
        
        return None
    except Exception:
        return None

def extract_outline(pdf_path):
    # Open the PDF using PyMuPDF
    doc = fitz.open(pdf_path)

    blocks = []  # This will store all text blocks with details

    # Loop through all pages of the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract text in dictionary format (includes font size and position)
        for b in page.get_text("dict")["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        # Save necessary text span info
                        blocks.append({
                            "text": s["text"].strip(),
                            "size": s["size"],          # Font size
                            "font": s["font"],          # Font name
                            "bold": "Bold" in s["font"],# Is bold font
                            "page": page_num + 1,       # 1-indexed page number
                            "y": s["bbox"][1]           # Y-position (for top-of-page detection)
                        })

    # Remove empty text spans
    blocks = [b for b in blocks if b["text"]]

    # Sort font sizes in descending order to detect title and heading levels
    sizes = sorted(set([b["size"] for b in blocks]), reverse=True)

    # Map top font sizes to heading levels
    size_to_level = {}
    if sizes:
        size_to_level[sizes[0]] = "title"  # Largest font size = Title
    if len(sizes) > 1:
        size_to_level[sizes[1]] = "H1"
    if len(sizes) > 2:
        size_to_level[sizes[2]] = "H2"
    if len(sizes) > 3:
        size_to_level[sizes[3]] = "H3"

    # Extract document title by collecting all blocks with the largest font size
    # that appear early in the document (first 3 pages)
    title_blocks = [
        b for b in blocks 
        if size_to_level.get(b["size"]) == "title" and b["page"] <= 3
    ]
    
    if title_blocks:
        # Group title blocks by line proximity (within 5 pixels vertically)
        title_lines = []
        current_line = []
        last_y = None
        
        # Sort by page and y-position to get proper order
        title_blocks.sort(key=lambda x: (x["page"], x["y"]))
        
        for block in title_blocks:
            if last_y is None or abs(block["y"] - last_y) <= 5:
                # Same line or very close
                current_line.append(block)
            else:
                # New line
                if current_line:
                    title_lines.append(current_line)
                current_line = [block]
            last_y = block["y"]
        
        # Add the last line
        if current_line:
            title_lines.append(current_line)
        
        # Concatenate all lines to form the complete title
        title_parts = []
        for line in title_lines:
            line_text = " ".join(block["text"] for block in line).strip()
            if line_text:
                title_parts.append(line_text)
        
        title = " ".join(title_parts).strip()
        # Clean up extra spaces
        title = " ".join(title.split())
        
        # If title is still too short, try OCR fallback
        if len(title) < 10:
            title = extract_title_with_ocr(doc) or title
    else:
        # No title blocks found, try OCR fallback
        title = extract_title_with_ocr(doc) or "Untitled"

    outline = []

    # Go through blocks and classify H1/H2/H3 based on size mapping
    for b in blocks:
        level = size_to_level.get(b["size"])

        # Filter only potential headings (based on logic below)
        if level in ["H1", "H2", "H3"] and is_potential_heading(b["text"]):
            outline.append({
                "level": level,
                "text": b["text"],
                "page": b["page"]
            })

    # If the document is a form (too many headings on page 1), ignore outline
    if len(outline) > 25 and all(h["page"] == 1 for h in outline):
        outline = []

    return {
        "title": title,
        "outline": outline
    }

def is_potential_heading(text):
    """
    Rule-based filter to determine if a text block is a real heading.
    Adjusted to avoid junk like "1.", "Rs.", etc.
    """
    if not text:
        return False
    if len(text) < 4:  # Too short
        return False
    if text.strip().isdigit():  # Only a number like "1." or "12."
        return False
    # if len(text.split()) > 25:  # Too long, likely a paragraph
    #     return False
    if len(text.strip()) <= 2:  # Single letter or abbreviation
        return False
    return True
