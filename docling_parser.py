from docling.document_converter import DocumentConverter

def parse_pdf(file_path, markdown_file_path):
    source = file_path  # document per local path or URL
    converter = DocumentConverter()
    result = converter.convert(source)
    with open(markdown_file_path, 'w') as f:
        f.write(result.document.export_to_markdown())