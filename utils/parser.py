from docling.document_converter import DocumentConverter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_core.output_parsers import JsonOutputParser
def parse_pdf(file_path, markdown_file_path):
    source = file_path  # document per local path or URL
    converter = DocumentConverter()
    result = converter.convert(source)
    with open(markdown_file_path, 'w') as f:
        f.write(result.document.export_to_markdown())


def parse_md(file_path):
    headers_to_split_on = [
        # ("#", "Header 1"),
        ("##", "Header 2"),
        # ("###", "Header 3"),
    ]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    with open(file_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    result = splitter.split_text(md_text)
    return result


def parse_json(input):
    json_parser = JsonOutputParser()
    try:
        parsed_json = json_parser.invoke(input)
    except Exception as e:
        print(f"Error occurred while parsing json: {e}")
        # TODO: only delete the concept that failed to parse
        return {}
    
    return parsed_json