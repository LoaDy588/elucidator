import argparse
import chevron
import yaml
import markdown
from distutils import dir_util, file_util
import os

MD_EXT = ['abbr', 'footnotes', 'fenced_code', 'tables', 'codehilite', 'toc', 'smarty', 'nl2br']

MD_EXT_CFG = {
    'footnotes' : {
        'PLACE_MARKER' : '[FOOTNOTES]'
    },
    'codehilite' : {
        'linenums' : False,
        'css_class' : 'code_highlight'
    },
    'toc' : {
        'marker' : '[TOC]',
        'title' : 'Table of Content',
    }
}

def load_config(root_dir):
    global_metadata = None
    static_dirs = None
    output_dir = None
    theme_dir = None

    with open(root_dir + "config.yaml", "r") as file:
        loaded_metadata = yaml.full_load(file)
        static_dirs = loaded_metadata.pop("static_dirs")
        output_dir = loaded_metadata.pop("output_dir")
        theme_dir = loaded_metadata.pop("theme_dir")
        global_metadata = loaded_metadata

    if output_dir[-1] != "/":
        output_dir += "/"

    if theme_dir[-1] != "/":
        theme_dir += "/"

    return global_metadata, static_dirs, output_dir, theme_dir
    

def split_file(input_path):
    input_file = open(input_path, 'r')
    for s in input_file:
        if s.startswith('---'):
            break
    
    yaml_lines = []
    for s in input_file:
        if s.startswith('---'):
            break
        else:
            yaml_lines.append(s)

    ym = ''.join(yaml_lines)
    md = ''.join(input_file)
    input_file.close()
    return ym, md


def generate_page(global_metadata, input_path, output_path, template):
    print("Creating:", output_path, "from:", input_path)
    
    ym, md = split_file(input_path)
    metadata = yaml.load(ym, yaml.Loader)
    metadata.update(global_metadata)
    metadata["content"] = markdown.markdown(md, extensions=MD_EXT, extension_configs = MD_EXT_CFG)

    dir_path = os.path.dirname(output_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    output_file = open(output_path, 'w')

    #chevron calls str object title as callable, this is a workaround
    # https://github.com/noahmorrison/chevron/issues/117
    if "title" in metadata:
        value = metadata["title"]
        metadata["title"] = dict({"title": value})

    html = chevron.render(template, metadata)
    output_file.write(html)
    output_file.close()


def main(root_dir):
    if root_dir[-1] != "/":
        root_dir += "/"
    
    print("Starting site generation...")
    print("Root dir is:", root_dir)

    global_metadata, static_dirs, output_dir, theme_dir = load_config(root_dir)
    
    print ("Output dir is:", output_dir)
    print ("Theme dir is:", theme_dir)

    # copy static content, if any and all folders and non .html files in theme
    print("Copying static dirs:", static_dirs)
    for item in static_dirs:
        dir_util.copy_tree(root_dir + "content/" + item, root_dir + output_dir + item, update=1)

    theme_content = next(os.walk(root_dir + theme_dir))
    for item in theme_content[1]:
        dir_util.copy_tree(root_dir + "theme/" + item, root_dir + output_dir + item, update=1)
    for item in theme_content[2]:
        if item.split(".")[1] != "html":
            file_util.copy_file(root_dir + "theme/" + item, root_dir + output_dir + item, update=1)

    # walk the content folder and generate html files    
    print("Starting .html file generation...")

    theme_index = open(root_dir + theme_dir + "index.html", 'r').read()
    theme_base = open(root_dir + theme_dir + "base.html", 'r').read()

    for root, dirs, files in os.walk(root_dir + "content/"):
        strip_level = root.replace(root_dir + "content/", "")
        for item in files:
            item_split = item.split(".")

            if item_split[1] == "md":
                output_path = root_dir + output_dir + strip_level + "/" + item_split[0] + ".html"
                input_path = root + "/" + item

                if root == root_dir + "content/" and item_split[0] == "index":
                    generate_page(global_metadata, input_path, output_path, theme_index)
                else:
                    generate_page(global_metadata, input_path, output_path, theme_base)
    print("Generation finished! Exiting...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple site generator.")
    parser.add_argument("root", help="root of site folder, defaults to current folder", nargs='?', default="./")
    parser.add_argument('--version', action='version', version='%(prog)s 0.3')
    args = parser.parse_args()
        
    main(vars(args)["root"])
