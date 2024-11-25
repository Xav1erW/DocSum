from langchain.prompts import PromptTemplate

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