import gradio as gr
from pyvis.network import Network
import tempfile

from doc_sum import SummaryAgent
from docling_parser import parse_pdf

# 示例知识图谱三元组
data = [
    ("实体1", "关系1", "实体2"),
    ("实体2", "关系2", "实体3"),
    ("实体3", "关系3", "实体4"),
    ("实体4", "关系4", "实体1"),
]

# 根据三元组构建知识图谱并生成交互式图
def build_interactive_graph(data):
    net = Network(height="750px", width="100%", directed=True)

    for source, relation, target in data:
        net.add_node(source, label=source, color="lightblue")
        net.add_node(target, label=target, color="lightblue")
        net.add_edge(source, target, label=relation)

    # 添加物理布局
    # net.toggle_physics(True)
    net.toggle_hide_edges_on_drag(True)
    net.toggle_physics(False)
    net.set_edge_smooth('discrete')

    html = net.generate_html()
    html = html.replace("'", "\"")

    return f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera;
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms
    allow-scripts allow-same-origin allow-popups
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen=""
    allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""

def all_summary(file)->tuple[str, str]:
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md') as temp:
        markdown_path = temp.name
        parse_pdf(file_path=file, markdown_file_path=markdown_path)
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md') as temp2:
        output_filename = temp2.name
        agent = SummaryAgent(markdown_path, output_filename)
        agent.run()
    
    with open(output_filename, 'r') as f:
        summary = f.read()

    kg = [
        ("实体1", "关系1", "实体2"),
        ("实体2", "关系2", "实体3"),
        ("实体3", "关系3", "实体4"),
        ("实体4", "关系4", "实体1"),
    ]
    kg_viz = build_interactive_graph(kg)
    return summary, kg_viz

# Gradio 回调函数
def generate_interactive_graph(triplets):
    try:
        triplets_list = [tuple(triplet.split(",")) for triplet in triplets.split("\n") if triplet.strip()]
        output_file = build_interactive_graph(triplets_list)
        return output_file
    except Exception as e:
        return f"错误: {str(e)}"

# Gradio 界面
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 知识图谱生成与交互展示工具")

    with gr.Row():
        # triplet_input = gr.Textbox(label="输入知识图谱三元组", 
        #                            placeholder="每行一个三元组，格式为: 实体1,关系,实体2",
        #                            lines=5)
        file_input = gr.File(label="上传文件", file_types=[".pdf", ".md"])

        output_box = gr.Textbox(label="总结", lines=10, interactive=False)
    
    output_html = gr.HTML(label="交互式知识图谱")

    generate_button = gr.Button("生成总结")

    generate_button.click(all_summary, inputs=file_input, outputs=[output_box, output_html])

# 启动应用
demo.launch()
