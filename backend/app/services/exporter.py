import logging
import re
from docx import Document

logger = logging.getLogger(__name__)


def export_md_to_docx(md_text: str, output_path: str) -> str:
    """
    Export markdown or plain text to DOCX format.
    Uses pure Python libraries (python-docx) - no external binaries required.
    """
    logger.info(f"Exporting markdown to DOCX: {output_path}")
    
    doc = Document()
    
    # Split text into blocks (paragraphs separated by double newlines)
    blocks = re.split(r'\n\s*\n', md_text.strip())
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Check if it's a markdown heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', block, re.MULTILINE)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            doc.add_heading(text, level=min(level, 6))
            continue
        
        # Check if it's a list (unordered or ordered)
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if lines:
            is_list = all(re.match(r'^[\*\-\+]\s+|\d+\.\s+', line) for line in lines)
            
            if is_list:
                for line in lines:
                    # Remove list markers
                    list_item = re.sub(r'^[\*\-\+]\s+|\d+\.\s+', '', line)
                    doc.add_paragraph(list_item, style='List Bullet')
                continue
        
        # Regular paragraph - handle inline formatting
        para = doc.add_paragraph()
        _add_formatted_text(para, block)
    
    doc.save(output_path)
    return ""


def _add_formatted_text(paragraph, text: str):
    """
    Add text to paragraph with markdown formatting (bold, italic).
    Handles **bold**, __bold__, *italic*, and _italic_ syntax.
    """
    # Simple approach: handle bold first, then italic
    # Pattern for bold: **text** or __text__
    bold_pattern = r'(\*\*|__)(.+?)\1'
    
    # Process bold first
    parts = []
    last_end = 0
    for match in re.finditer(bold_pattern, text):
        if match.start() > last_end:
            parts.append(('text', text[last_end:match.start()]))
        parts.append(('bold', match.group(2)))
        last_end = match.end()
    
    if last_end < len(text):
        parts.append(('text', text[last_end:]))
    
    if not parts:
        parts = [('text', text)]
    
    # Now process each part for italic
    for part_type, part_text in parts:
        if part_type == 'bold':
            run = paragraph.add_run(part_text)
            run.bold = True
        else:
            # Check for italic in the text part
            italic_pattern = r'(?<!\*)(?<![a-zA-Z0-9_])(\*|_)([^*_\s]+?)\1(?![*_])'
            italic_matches = list(re.finditer(italic_pattern, part_text))
            
            if not italic_matches:
                paragraph.add_run(part_text)
            else:
                last_italic_end = 0
                for match in italic_matches:
                    if match.start() > last_italic_end:
                        paragraph.add_run(part_text[last_italic_end:match.start()])
                    run = paragraph.add_run(match.group(2))
                    run.italic = True
                    last_italic_end = match.end()
                if last_italic_end < len(part_text):
                    paragraph.add_run(part_text[last_italic_end:])

