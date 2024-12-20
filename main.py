import json
import os
from repo import Repo
from json_to_xmi import JsonToXmiConverter
from pom_xml_to_json import pom_xml_to_json, generate_dot_graph
from compare_xmi_trees import parse_xmi, find_common_projects
# from gradle_to_json import gradle_to_json
from parse_gradle_dependencies import gradle_to_json

separator_string = "-------------------------------"

def convert_dependency_json_from_repo(project_name: str, repo: Repo):
    print(separator_string)
    json_path = ""
    if repo.is_pom:
        print("Converting pom.xml file to JSON...")
        json_path = pom_xml_to_json(project_name, repo.config_file, repo.local_repo_dir)
        print(f"{project_name} JSON created in {json_path}")

    if repo.is_gradle:
        print("Converting gradle file to JSON...")
        # json_path = generate_json_from_gradle(project_name, repo.config_file, repo.local_repo_dir)
        # res = generate_json_from_gradle(repo.local_repo_dir)
        json_path = gradle_to_json(repo.local_repo_dir)

    print(separator_string)
    return json_path

def convert_json_dependency_to_xmi(repo_name: str, dependency_json_path: str, file_path: str):
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


    return_path = os.path.join(file_path, dependency_xmi_path)

    return dependency_xmi_path


def compare_trees(repo_path_1, path_xmi_1, repo_path_2, path_xmi_2):
    print(separator_string)
    print("Comparing trees...")
    try:
        model1 = os.path.join(repo_path_1, path_xmi_1)
        with open(model1, 'r', encoding='utf-8') as file1:
            content1 = file1.read()

        model2 = os.path.join(repo_path_2, path_xmi_2)
        with open(model2, 'r', encoding='utf-8') as file2:
            content2 = file2.read()

        # Parse both XMI contents
        projects1 = parse_xmi(content1)
        projects2 = parse_xmi(content2)
        print("XMIs parsed")
        print("Finding common dependencies...")
        # Find and print common projects
        common = find_common_projects(projects1, projects2)
        print(f"Number of common projects: {len(common)}")
        # print("Common project names:")
        # for name in common:
        #     print(name)
        print(separator_string)
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")




def create_xmi_from_url(repo_name: str, url: str):
    repo = Repo(repo_name, url, github_token)
    json_path = convert_dependency_json_from_repo(repo_name, repo)
    xmi_path = convert_json_dependency_to_xmi(repo_name, json_path, repo.local_repo_dir)
    return repo, json_path, xmi_path

# project_path = "/Users/macbookpro/PycharmProjects/Dependency-Tree-Comparison/depgraph-maven-plugin-test"
# json_path = convert_dependency_json("Test", project_path)
# convert_json_dependency_to_xmi("Test", json_path)

github_token = "1234"

# repo_url = "https://github.com/graphhopper/graphhopper"
# repo_name = "graphhopper"
# repo = Repo(repo_name, repo_url, github_token)
# repo.print_status()
# json_path = convert_dependency_json_from_repo(repo_name, repo)
# graphhopper_xmi = convert_json_dependency_to_xmi(repo_name, json_path)
# generate_dot_graph(repo)




besu_repo, besu_json_path, besu_xmi = create_xmi_from_url("besu", "https://github.com/hyperledger/besu")
teku_repo, teku_json, teku_xmi = create_xmi_from_url("teku", "https://github.com/Consensys/teku")

compare_trees(teku_repo.local_repo_dir, teku_xmi, besu_repo.local_repo_dir, besu_xmi)


# test_url = "https://github.com/ferstl/depgraph-maven-plugin/"
# project_name = "depgraph-maven-plugin"
# repo, json_path = generate_dependency_json(project_name, test_url)
# convert_json_dependency_to_xmi(project_name, json_path)

# petclinic_repo, petclinic_json_path, xmi_path = create_xmi_from_url("PetClinic", "https://github.com/spring-projects/spring-petclinic")