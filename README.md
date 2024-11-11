# DocSum Agent

本项目是一个智能代理（Agent），旨在自动生成长文档的摘要。通过自然语言处理技术，Agent 能够高效处理并提取文本中的核心内容，帮助用户快速获取关键信息。

## 初步设想

文档理解总结agent：
1. 文档按章节分割
	1. pdf的书签分割
	2. markdown的类似 `### header3` 标记分割
	3. 按照特定标记规则分割，比如 `/^\d+(\.\d+)?\s+[Ss]ection\s+\w+` 
	4. 通过LLM直接分割（可能面临文本过长的问题，或许需要预分割成大的块）
2. 章节内容的总结
	1. 章节新提出的概念的提取，存到数据库中
	2. 章节中提及的前文中定义的概念或实体，需要从前文把概念检索加入LLM的prompt
	3. 之前章节的，或者文章整体结构的简介（需要简短，只需要知道每个章节都有什么内容，有些时候总结可能需要整体结构）
	4. 根据以上信息总结出最终的章节总结
3. 循环上述过程得到最后的文档理解与总结

总体上仿照人类（我的）阅读习惯，先看整体结构，之后按照章节阅读，记忆新提出的概念，当后文提及时去前文查找。

初步可以只搭建一个不对概念存储和查找的框架，只是实现分割和循环总结，最终拼接的流程。

## 工具选用

文档解析：
* [docling](https://github.com/DS4SD/docling/tree/main)

智能体：
* [LangChain](https://github.com/hwchase17/langchain)

智能体模型：
* [Qwen2-1.5B](https://huggingface.co/Qwen/Qwen2-1.5B-Instruct)  小模型
* [Qwen2-7B](https://huggingface.co/Qwen/Qwen2-7B-Instruct)  较大模型