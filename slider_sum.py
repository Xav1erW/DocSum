# 根据doc_sum生成的总结生成marp格式的幻灯片
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.parser import parse_md

marp_generate_prompt = PromptTemplate(
    input_variables=["prev_slider", "chapter_summary"],
    template="""
根据如下指引生成符合marp格式的幻灯片:
**主题**： 使用 Markdown 语法创建精美的演示文稿，轻松取代 LaTeX Beamer！
**目标**： 生成包含基本语法、格式控制、分栏、列表、字体控制等内容的 Marp slider。
**内容**：
1. **Markdown 基础语法**：
    * 标题：`#`、`##`、`###` 等依次递增，表示不同级别的标题。
    * 粗体：`**粗体**`。
    * 斜体：`*斜体*`。
    * 删除线：`~~删除线~~`。
    * 分割线：`---`。
    * 超链接：`[链接文字](链接地址)`。
    * 引用：`>`。
    * 列表：`-` 或 `1. `。
    * 代码块：缩进四个空格或使用反引号包裹。
    * 脚注：`[^1]` / `[^1]:`。
    * 待办事项：`[ ]` / `[x]`。
2. **格式控制**：
    * 页面分栏：使用 `<!-- _class: cols-2 -->` 等指令设置不同分栏方式，例如 `cols-2`（两列）、`cols-3`（三列）等。
    * 列表分列：使用 `<!-- _class: cols2_ol_sq -->` 等指令设置不同列表样式，例如 `cols2_ol_sq`（两列有序列表+方形序号）、`cols2_ul_ci`（两列无序列表+圆形序号）等。
    * 引用盒子：使用 `<!-- _class: bq-purple -->` 等指令设置不同颜色的引用框，例如 `bq-purple`（紫色）、`bq-blue`（蓝色）等。
    * 导航栏：使用 `<!-- _class: navbar -->` 指令创建导航栏，并使用 `\\` 开头，粗体表示当前活动标题，斜体表示其他标题。
    * 固定标题行：使用 `<!-- _class: fixedtitleA -->` 或 `<!-- _class: fixedtitleB -->` 指令使标题固定在顶部。
    * 脚注：使用 `<!-- _class: footnote -->` 指令创建脚注，并使用 `<div class="tdiv"></div>` 和 `<div class="bdiv"></div>` 分别包裹正文内容和脚注内容。
    * 调节字体大小：使用 `<!-- _class: tinytext -->`、`<!-- _class: smalltext -->`、`<!-- _class: largetext -->`、`<!-- _class: hugetext -->` 等指令调节字体大小。
    * 图表标题：使用 `<div class="caption">标题文字</div>` 定义图表标题。
3. **其他**：
    * 图片：使用 `![图片描述](图片地址)` 插入图片，支持本地路径和网络路径。
    * 数学公式：使用 `$...$` 插入行内公式，使用 `$$...$$` 插入行间公式。
    * HTML 元素：支持使用 `<br>`、`<hr>`、`<b></b>`、`<i></i>`、`<kbd></kbd>` 等标签。
**示例**：
```markdown
---
marp: true
size: 16:9
theme: am_blue
paginate: true
headingDivider: [2,3]
footer: *初虹（虹鹄山庄）* *Awesome Marp：轻松取代 LaTeX Beamer！* *2024年1月13日（v1.3）*
---
# 演示文稿标题
## 目录
- [关于模板](#3)
- [封面页](#10) 
- [目录页](#16)
- [页面分栏与列表分列](#20)
- [引用、链接和引用盒子](#38)
- [导航栏](#45)
- [其他自定义样式](#48)
- [需要知道的基础知识](#56)
- [最后一页](#59)
---
## 页面分栏示例
<!-- _class: cols-2 -->
<div class=ldiv>  
第一列（左侧栏）的内容在这里
内容可以是普通纯文本，可以是列表，也可以是引用块、链接、图片等
</div>
<div class=rdiv>
第二列（右侧栏）的内容在这里
</div>
---
## 列表分列示例
<!-- _class: cols2_ol_sq fglass -->
- 列表项 1
- 列表项 2
- 列表项 3
---
## 引用盒子示例
<!-- _class: bq-purple -->
> 引用内容
>
> 引用内容
---
## 导航栏示例
<!-- _class: navbar -->
<!-- _header: \\ ***@Awesome Marp*** *关于模板* *封面页* *目录页* *分栏与分列* *引用盒子* **导航栏** *基础知识* -->
---
## 固定标题行示例
<!-- _class: fixedtitleA -->
- 固定标题行内容
---
## 脚注示例
<!-- _class: footnote -->
<div class="tdiv">
正文内容
</div>
<div class="bdiv">
1. 脚注内容
</div>
---
## 调节字体大小示例
<!-- _class: largetext -->
- 大字体内容
---
## 图表标题示例
![图片描述](图片地址)
<div class="caption">
图表标题
</div>
```
**提示**：
* 可以根据需要修改主题、页码、标题分割方式等参数。
* 可以参考 Awesome Marp 主题提供的样式，例如封面页、目录页等。

根据以上给出的格式说明，针对如下章节内容，生成章节内容的幻灯片，控制在2-3页。同时会给出之前章节的slider内容，请在此内容基础上继续生成。如果之前章节幻灯片内容为空，意味着这是第一章，请生成封面和目录页。


之前章节幻灯片：
{prev_slider}
当前章节内容：
{chapter_summary}
""",
)

# 初始化OpenAI模型和LLMChain
llm_small = ChatOpenAI(model="glm-4-flash", base_url="https://one-api.x-wang.tech/v1")  # 你可以根据需要选择其他模型
llm_big = ChatOpenAI(model="glm-4-flash", base_url="https://one-api.x-wang.tech/v1")  # 你可以根据需要选择其他模型

output_parser = StrOutputParser()

single_chapter_generate_chain = marp_generate_prompt | llm_small | output_parser

def generate_single_chapter_slider(chapter_text, prev_slider):
    return single_chapter_generate_chain.invoke({
        "prev_slider": prev_slider,
        "chapter_summary": chapter_text,
    })

def generate_slider_from_markdown(markdown_file_path, output_file):
    markdown_chapters = parse_md(markdown_file_path)

    sliders = ['']
    for chapter_text in tqdm(markdown_chapters):
        chapter_slider = generate_single_chapter_slider(chapter_text, sliders[-1])
        sliders.append(chapter_slider)
    
    final_slider = '\n\n'.join(sliders)
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(final_slider)


if __name__ == "__main__":
    markdown_file_path = "temp/11out_sum-zh.md"
    output_file = "temp/slider.md"
    generate_slider_from_markdown(markdown_file_path, output_file)