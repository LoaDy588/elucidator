import argparse
import chevron
import yaml
import markdown
from distutils import dir_util
import os


def load_config(root_dir):
    global_metadata = None
    static_dirs = None
    output_dir = None

    with open(root_dir + "config.yaml", "r") as file:
        loaded_metadata = yaml.full_load(file)
        static_dirs = loaded_metadata["static_dirs"]
        output_dir = loaded_metadata["output_dir"]
        loaded_metadata.pop("static_dirs")
        loaded_metadata.pop("output_dir")
        global_metadata = loaded_metadata

    if output_dir[-1] != "/":
        output_dir += "/"

    return global_metadata, static_dirs, output_dir
    

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
    print("Creating:", output_path, "from:", input_path, ", with template:", template)
    
    ym, md = split_file(input_path)
    metadata = yaml.load(ym, yaml.Loader)
    metadata.update(global_metadata)
    metadata["content"] = markdown.markdown(md)

    template_file = open(template, 'r')
    output_file = open(output_path, 'w')
    
    html = chevron.render(template_file, metadata)
    output_file.write(html)

    template_file.close()
    output_file.close()


def main(root_dir):
    if root_dir[-1] != "/":
        root_dir += "/"
    
    print("Starting site generation...")
    print("Root dir is:", root_dir)

    global_metadata, static_dirs, output_dir = load_config(root_dir)
    
    print ("Output dir is:", output_dir)

    # copy static content, if any and all folders in theme
    print("Copying static dirs:", static_dirs)
    for item in static_dirs:
        dir_util.copy_tree(root_dir + "content/" + item, output_dir + item, update=1)

    for item in next(os.walk('./theme/'))[1]:
        dir_util.copy_tree(root_dir + "theme/" + item, output_dir + item, update=1)
    
    # walk the content folder and generate html files    
    print("Starting .html file generation...")
    for root, dirs, files in os.walk(root_dir + "content/"):
        strip_level = root[10:] + "/"
        
        for item in files:
            item_split = item.split(".")

            if (item_split[1] == "md"):
                output_path = output_dir + strip_level + item_split[0] + ".html"
                input_path = root + "/" + item

                if root == "./content/" and item_split[0] == "index":
                    generate_page(global_metadata, input_path, output_path, root_dir + "theme/index.html")
                else:
                    generate_page(global_metadata, input_path, output_path, root_dir + "theme/base.html")

    print("Generation finished! Exiting...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple site generator.")
    parser.add_argument("root", help="root of site folder, defaults to current folder", nargs='?', default="./")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()
        
    main(vars(args)["root"])