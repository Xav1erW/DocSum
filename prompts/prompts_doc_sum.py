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
# You are reading a chapter of text. Your task is to provide a comprehensive summary of the chapter's content, focusing on the main ideas, arguments, and significant points made by the author. While you should take note of any new concepts introduced, your primary goal is to capture the essence of the chapter's narrative and message. 
    template="""
You are provided with a textual excerpt from a chapter and explanations of concepts that may be related to this chapter. Your task is to summarize the content of the chapter by integrating the information given in the text and the explanations of the concepts. The summary should capture the main ideas, highlight key points, and reflect the significance of the concepts mentioned. Ensure that the summary is coherent, concise, and provides a comprehensive overview of the chapter's content.

Please adhere to the following guidelines:

Focus on the central theme and core message of the chapter.
Include relevant concepts and explain how they relate to the chapter's content.
Maintain academic integrity and objectivity in your summary.
Aim for clarity and brevity while ensuring no loss of critical information.

你是一个擅长总结长文本的助手，能够总结用户给出的文本，并生成摘要。你的任务是生成简洁流畅的中文摘要，每章最长不可超过原文的10%生成的格式如下：

## Chapter Title
Please omit this section if there is no newly introduced concept or entity closely related to the topic.
concepts or entities ：A brief description of the concept or entity, ensuring it is newly introduced in this chapter.

Summary of the chapter.

use Chinese to write the summary.
使用中文总结

Chapter Text:
{chapter_text}

Concept Explanations:
{concepts_dict}
"""
)

triple_generation_prompt = PromptTemplate(
    input_variables=["concepts_text"],
    template="""Based on the following concepts and their explanations, generate knowledge triples in the format:

[
    ["Entity1", "Relation1", "Entity2"],
    ["Entity2", "Relation2", "Entity3"],
    ["Entity3", "Relation3", "Entity4"],
    ...
]

Instructions:
1. Entities must be concise, preferably single nouns or short noun phrases.
2. Entities should avoid being sentences, descriptions, or overly long phrases.
3. Relations should clearly describe the relationship between the two entities in no more than 3 words.
4. The output must be a valid JSON array and strictly follow the specified format.

Concept Explanations:
{concepts_text}
"""
)



