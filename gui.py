import gradio as gr
from pyvis.network import Network
import json
import tempfile

from doc_sum import SummaryAgent
from utils.parser import parse_pdf

def load_triplets(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_interactive_graph(data):
    net = Network(height="750px", width="100%", directed=True)
    
    # 添加节点和边
    for source, relation, target in data:
        net.add_node(source, label=source, color="lightblue", size=10)
        net.add_node(target, label=target, color="lightblue", size=10)
        net.add_edge(source, target, label=relation)
    
    # 启用物理布局并设置参数
    net.toggle_physics(True)
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08,
          "avoidOverlap": 1
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "enabled": true,
          "iterations": 200
        }
      }
    }
    """)

    html = net.generate_html()
    html = html.replace("'", "\"")

    return f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera;
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms
    allow-scripts allow-same-origin allow-popups
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen=""
    allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""


def all_summary(file)->tuple[str, str]:
    file_suffix = file.split('.')[-1]
    if file_suffix == 'pdf':
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md') as temp:
            markdown_path = temp.name
            parse_pdf(file_path=file, markdown_file_path=markdown_path)
    else:
        markdown_path = file
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md') as temp2:
        output_filename = temp2.name
        agent = SummaryAgent(markdown_path, output_filename)
        agent.run()
   
    with open(output_filename, 'r') as f:
        summary = f.read()

    triples_output_file = output_filename.replace(".md", "_triples.json")
    triplets = load_triplets(triples_output_file)
    kg_viz = build_interactive_graph(triplets)
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
