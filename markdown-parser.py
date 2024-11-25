from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter

headers_to_split_on = [
    # ("#", "Header 1"),
    ("##", "Header 2"),
    # ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

with open('out.md', 'r') as f:
    text = f.read()

result = splitter.split_text(text)

print(result)

# print('First two chunks:')
# print('-'*40)
# print(result[0])
# print('-'*40)
# print(result[1])