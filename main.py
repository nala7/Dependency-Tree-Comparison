import json
import os
from repo import Repo
from json_to_xmi import JsonToXmiConverter
from pom_xml_to_json import pom_xml_to_json, generate_dot_graph
from compare_xmi_trees import parse_xmi, find_common_projects

separator_string = "-------------------------------"

def convert_dependency_json_from_repo(project_name: str, repo: Repo):
    print(separator_string)
    print("Converting pom.xml file to JSON...")
    json_path = pom_xml_to_json(project_name, repo.config_file, repo.local_repo_dir)
    print(f"{project_name} JSON created in {json_path}")
    print(separator_string)
    return json_path


def convert_dependency_json(project_name: str, project_path: str):
    print(separator_string)
    pom_file_path = os.path.join(project_path, "pom.xml")

    if not os.path.exists(pom_file_path):
        raise FileNotFoundError(f"pom.xml not found in the specified project path: {project_path}")

    # Read the content of the pom.xml file
    with open(pom_file_path, 'r', encoding='utf-8') as file:
        pom_file = file.read()

    print("Converting pom.xml file to JSON...")
    json_path = pom_xml_to_json(project_name, pom_file, project_path)
    print(f"{project_name} JSON created in {json_path}")
    print(separator_string)
    return json_path


def convert_json_dependency_to_xmi(repo_name: str, dependency_json_path: str):
    print(separator_string)
    print("Converting to XMI...")
    try:
        with open(dependency_json_path, 'r') as file:
            json_data = json.load(file)
            print(json_data[0], json_data[1], json_data[2])
    except Exception as e:
        print(f"JSON could not be loaded for {dependency_json_path}")

    xmi_output = JsonToXmiConverter.convert_json_to_xmi(json_data)

    dependency_xmi_path = f"{repo_name}.xmi"

    with open(dependency_xmi_path, 'w') as file:
        file.write(xmi_output)

    print(f"{repo_name} XMI created in {dependency_xmi_path}")
    print(separator_string)

    return dependency_xmi_path


def compare_trees(path_xmi1, path_xmi2):
    try:
        # Open the first XMI file and parse
        with open(path_xmi1, 'r', encoding='utf-8') as file1:
            content1 = file1.read()

        # Open the second XMI file and parse
        with open(path_xmi2, 'r', encoding='utf-8') as file2:
            content2 = file2.read()

        # Parse both XMI contents
        projects1 = parse_xmi(content1)
        projects2 = parse_xmi(content2)

        # Find and print common projects
        common = find_common_projects(projects1, projects2)
        print(f"Number of common projects: {len(common)}")
        print("Common project names:")
        for name in common:
            print(name)

    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
# project_path = "/Users/macbookpro/PycharmProjects/Dependency-Tree-Comparison/depgraph-maven-plugin-test"
# json_path = convert_dependency_json("Test", project_path)
# convert_json_dependency_to_xmi("Test", json_path)

github_token = "1234"

repo_url = "https://github.com/graphhopper/graphhopper"
repo_name = "graphhopper"
repo = Repo(repo_name, repo_url, github_token)
repo.print_status()
json_path = convert_dependency_json_from_repo(repo_name, repo)
graphhopper_xmi = convert_json_dependency_to_xmi(repo_name, json_path)
generate_dot_graph(repo)





compare_trees(graphhopper_xmi)


# test_url = "https://github.com/ferstl/depgraph-maven-plugin/"
# project_name = "depgraph-maven-plugin"
# repo, json_path = generate_dependency_json(project_name, test_url)
# convert_json_dependency_to_xmi(project_name, json_path)
