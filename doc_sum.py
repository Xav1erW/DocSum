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
from prompts.prompts_doc_sum import extract_concepts_prompt, concepts_retriever_prompt, chapter_summarize_prompt, triple_generation_prompt

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# set_debug(True)

class SummaryAgent:

    def __init__(self, input_markdown, output_path):
        # 初始化OpenAI模型和LLMChain
        self.llm_small = ChatOpenAI(model="yi-lightning", base_url="https://api.lingyiwanwu.com/v1")  # 你可以根据需要选择其他模型
        self.llm_big = ChatOpenAI(model="yi-lightning", base_url="https://api.lingyiwanwu.com/v1")  # 你可以根据需要选择其他模型
        
        # self.llm_small = ChatZhipuAI(
        #     model="glm-4-flash",
        #     temperature=0.5,
        #     api_key="2871338644afc60d738a128ae018735c.w6pc5DJVDl57nR6M"
        # )
        # self.llm_big = ChatZhipuAI(
        #     model="glm-4-flash",
        #     temperature=0.5,
        #     api_key="2871338644afc60d738a128ae018735c.w6pc5DJVDl57nR6M"
        # )
        
        self.output_parser = StrOutputParser()
        self.json_parser = JsonOutputParser()

        self.input_markdown = input_markdown
        self.output_path = output_path


        # 假设你有一个数据库用来存储概念，下面用字典代替
        self.concepts_dict = {}

        self.concepts_extractor = extract_concepts_prompt | self.llm_small | parse_json | self.store_concepts_to_db

        self.concepts_retriever = concepts_retriever_prompt | self.llm_small | self.json_parser | self.get_previous_concepts

        self.chapter_summarizer = chapter_summarize_prompt | self.llm_big | self.output_parser 

        self.triple_generator = triple_generation_prompt | self.llm_big | parse_json

    def store_concepts_to_db(self, concepts:dict):
        self.concepts_dict.update(concepts)
        return concepts

    # 4. 章节中提及的前文中定义的概念或实体，加入LLM的prompt
    def get_previous_concepts(self, concept_needed:list[str]):
        filtered_concepts = [{concept: self.concepts_dict.get(concept, "")} for concept in concept_needed]
        concepts_json = json.dumps(filtered_concepts)
        return concepts_json
    
    def generate_triples(self):
        concepts_text = json.dumps(self.concepts_dict)
        triples = self.triple_generator.invoke({
            "concepts_text": concepts_text
        })
        return triples

    def summarize_single_chapter(self, chapter_text):
        self.concepts_extractor.invoke({
            "chapter_text": chapter_text,
        })
        concepts_needed = self.concepts_retriever.invoke({
            "chapter_text": chapter_text,
            "concepts_list": json.dumps(list(self.concepts_dict.keys())),
        })
        chapter_sum = self.chapter_summarizer.invoke({
            "chapter_text": chapter_text,
            "concepts_dict": concepts_needed,
        })
        return chapter_sum


    # 主函数执行
    def run(self):
        markdown_path, output_file = self.input_markdown, self.output_path
        
        # 分割文档为章节
        chapters = parse_md(markdown_path)
        summaries = []

        # 循环处理每个章节
        try:
            for i, chapter in enumerate(chapters):
                print(f"总结第{i+1}章:")
                # print("raw_text")
                if chapter.metadata.get('Header 2', '') == '':
                    continue
                formatted_chapter = f"## {chapter.metadata.get('Header 2', '')}\n\n{chapter.page_content}"
                # print(formatted_chapter)
                summary = self.summarize_single_chapter(formatted_chapter)
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

        # 利用概念构建三元组
        print("\n开始生成三元组:")
        triples = self.generate_triples()
        print("\n生成的三元组:")
        print(triples)
        triples_output_file = output_file.replace(".md", "_triples.json")
        with open(triples_output_file, "w", encoding='utf-8') as f:
            json.dump(triples, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    markdown_path = './temp/11-chapter.md'
    # parse_pdf('第十一章[1].pdf', markdown_path)
    # main(markdown_path, '11out_sum-zh.md')
