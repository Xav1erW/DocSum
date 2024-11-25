import re
import json
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import os
# from langchain.globals import set_debug
from dotenv import load_dotenv
load_dotenv()

from docling_parser import parse_pdf

# set_debug(True)

# 初始化OpenAI模型和LLMChain
llm_small = ChatOpenAI(model="glm-4-flash", base_url="https://one-api.x-wang.tech/v1")  # 你可以根据需要选择其他模型
llm_big = ChatOpenAI(model="glm-4-flash", base_url="https://one-api.x-wang.tech/v1")  # 你可以根据需要选择其他模型

output_parser = StrOutputParser()
json_parser = JsonOutputParser()
# 假设你有一个数据库用来存储概念，下面用字典代替
concepts_dict = {}

extract_concepts_prompt = PromptTemplate(
    input_variables=["chapter_text"],
    template="""You are reading a chapter of text. Your task is to extract concepts or entities that are newly introduced in this chapter. These concepts or entities may not be fully understood before reading this chapter, and they could be crucial for understanding the next chapter. Please list each concept or entity with the following json structure:

{{
  "concept_name1": "A brief description of the concept or entity.",
  "concept_name2": "A brief description of the concept or entity.",
  ...
}}

Onlt give me the raw legal json string without other text. Do not include any special symbols in json keys.

Chapter text:
{chapter_text}

Please list all newly introduced concepts or entities in the order they appear in the chapter.
"""
)

concepts_retriever_prompt = PromptTemplate(
    input_variables=["chapter_text", "concepts_list"],
    template="""
You are tasked with reading the following chapter text. As you read, please identify any concepts or entities that you do not fully understand or are uncertain about. These could be concepts you haven't encountered before or ones whose meanings are not clear in this context. These concepts will be searched from a concept set. The available concepts are listed:
{concepts_list}

Chapter text:
{chapter_text}

Please list all concepts or entities you are unsure about in the order they appear in the chapter. Only list those that are appeared in the concepts list.
Please list all the needed concepts or entities with the following json structure:
[
    "concept1",
    "concept2",
    ...
]
Onlt give me the raw json string without other text.
""")

chapter_summarize_prompt = PromptTemplate(
    input_variables=["chapter_text", "concepts_dict"],
    template="""
Summarize the core content of the following chapter based on the provided text and the given concept explanations. Focus on the application of each concept and their relationships within the chapter. Try to distill the main ideas and key information. If necessary, use LaTeX equations to explain key concepts or results in a more precise and formal way. Please output the result in the following markdown format:

## chapter title
summary of the chapter

使用中文回答我总结的章节，请使用中文。

Chapter Text:
{chapter_text}

Concept Explanations:
{concepts_dict}
""")

def parse_json(input):
    try:
        parsed_json = json_parser.invoke(input)
    except Exception as e:
        print(f"Error occurred while parsing json: {e}")
        # TODO: only delete the concept that failed to parse
        return {}
    
    return parsed_json
def store_concepts_to_db(concepts:dict):
    global concepts_dict
    concepts_dict.update(concepts)
    return concepts


# 4. 章节中提及的前文中定义的概念或实体，加入LLM的prompt
def get_previous_concepts(concept_needed:list[str]):
    filtered_concepts = [{concept: concepts_dict.get(concept, "")} for concept in concept_needed]
    concepts_json = json.dumps(filtered_concepts)
    return concepts_json

concepts_extractor = extract_concepts_prompt | llm_small | parse_json | store_concepts_to_db

concepts_retriever = concepts_retriever_prompt | llm_small | json_parser | get_previous_concepts

chapter_summarizer = chapter_summarize_prompt | llm_big | output_parser 

def summarize_single_chapter(chapter_text):
    concepts_extractor.invoke({
        "chapter_text": chapter_text,
    })
    concepts_needed = concepts_retriever.invoke({
        "chapter_text": chapter_text,
        "concepts_list": json.dumps(list(concepts_dict.keys())),
    })

    chapter_sum = chapter_summarizer.invoke({
        "chapter_text": chapter_text,
        "concepts_dict": concepts_needed,
    })
    return chapter_sum

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
# 主函数执行
def main(markdown_path, output_file):
    # 分割文档为章节
    chapters = parse_md(markdown_path)
    summaries = []

    # 循环处理每个章节
    try:
        for i, chapter in enumerate(chapters):
            print(f"总结第{i+1}章:")
            print("raw_text")
            if chapter.metadata.get('Header 2', '') == '':
                continue
            formatted_chapter = f"## {chapter.metadata.get('Header 2', '')}\n\n{chapter.page_content}"
            print(formatted_chapter)
            summary = summarize_single_chapter(formatted_chapter)
            summaries.append(summary)
    except Exception as e:
        print(f"Error occurred while processing the chapter.: {e}")
        print("Generating summary from previous chapters.")

    # 最终生成完整的文档总结
    # final_summary = generate_document_summary(markdown_text)
    final_summary = '\n\n'.join(summaries)
    print("\n最终文档总结:")
    print(final_summary)
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(final_summary)

if __name__ == "__main__":
    markdown_path = '11-chapter.md'
    parse_pdf('第十一章[1].pdf', markdown_path)
    main(markdown_path, '11out_sum-zh.md')
