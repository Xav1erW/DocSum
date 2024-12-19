import re
import json
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import os
# from langchain.globals import set_debug
from dotenv import load_dotenv
load_dotenv()

from docling_parser import parse_pdf
from utils.parser import parse_md, parse_json
from prompts.prompts_doc_sum import extract_concepts_prompt, concepts_retriever_prompt, chapter_summarize_prompt

# set_debug(True)

# 初始化OpenAI模型和LLMChain
llm_small = ChatOpenAI(model="yi-lightning", base_url="https://api.lingyiwanwu.com/v1")  # 你可以根据需要选择其他模型
llm_big = ChatOpenAI(model="yi-lightning", base_url="https://api.lingyiwanwu.com/v1")  # 你可以根据需要选择其他模型

output_parser = StrOutputParser()
json_parser = JsonOutputParser()

# 假设你有一个数据库用来存储概念，下面用字典代替
concepts_dict = {}

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
    markdown_path = './temp/11-chapter.md'
    # parse_pdf('第十一章[1].pdf', markdown_path)
    main(markdown_path, '11out_sum-zh.md')
