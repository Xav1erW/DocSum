from langchain.prompts import PromptTemplate

extract_concepts_prompt = PromptTemplate(
    input_variables=["chapter_text"],
    template="""You are reading a chapter of text. Your task is to extract concepts or entities that are newly introduced in this chapter. These concepts or entities should not be fully understood prior to reading this chapter and could be essential for comprehending the following chapters. List each concept or entity with the following JSON structure:

{{
  "concept_name1": "A brief description of the concept or entity, ensuring it is newly introduced in this chapter.",
  "concept_name2": "A brief description of the concept or entity, ensuring it is newly introduced in this chapter.",
  ...
}}

Only provide the raw legal JSON string without any additional text. Do not include any special characters in the JSON keys.

Chapter Text:
{chapter_text}

List all newly introduced concepts or entities in the order they appear in the chapter.
"""
)


concepts_retriever_prompt = PromptTemplate(
    input_variables=["chapter_text", "concepts_list"],
    template="""
You are tasked with reading the following chapter text. As you read, identify any concepts or entities that you do not fully understand or are uncertain about. These could be concepts not previously encountered or ones whose meanings are unclear in this context. These concepts will be cross-referenced with a provided concept set. The available concepts are listed below:
{concepts_list}

Chapter Text:
{chapter_text}

List all concepts or entities you are unsure about in the order they appear in the chapter. Only list those that are present in the concepts list.
Please list the needed concepts or entities with the following JSON structure:
[
    "concept1",
    "concept2",
    ...
]
Only provide the raw JSON string without any additional text.
"""
)



chapter_summarize_prompt = PromptTemplate(
    input_variables=["chapter_text", "concepts_dict"],
    template="""
You are reading a chapter of text. Your task is to provide a comprehensive summary of the chapter's content, focusing on the main ideas, arguments, and significant points made by the author. While you should take note of any new concepts introduced, your primary goal is to capture the essence of the chapter's narrative and message. 
你是一个擅长总结长文本的助手，能够总结用户给出的文本，并生成摘要。你的任务是生成简洁流畅的中文摘要，每章最长不可超过原文的10%生成的格式如下：

## Chapter Title
Please omit this section if there is no newly introduced concept or entity closely related to the topic.
concepts or entities ：A brief description of the concept or entity, ensuring it is newly introduced in this chapter.

Summary of the chapter.


Chapter Text:
{chapter_text}

Concept Explanations:
{concepts_dict}
"""
)


