import json
import os
from repo import Repo
from json_to_xmi import JsonToXmiConverter
from pom_xml_to_json import pom_xml_to_json, generate_dot_graph
from compare_xmi_trees import compare_trees
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


def compare(repo1: Repo, path_xmi_1, repo2: Repo, path_xmi_2):
    print(separator_string)
    print("Comparing trees...")

    model1 = os.path.join(repo1.local_repo_dir, path_xmi_1)
    model2 = os.path.join(repo2.local_repo_dir, path_xmi_2)
    common_count, common_projects = compare_trees(repo1.name, model1, repo2.name, model2)
    print(f"Number of common projects: {common_count}")
    # print("Common project names:")
    # for name in common_projects:
    #     print(name)
    print(separator_string)




def create_xmi_from_url(repo_name: str, url: str):
    dates = ["12/2023", "12/2024"]
    repo = Repo(repo_name, url, github_token)
    json_list = []
    xmi_list = []
    for date in dates:
        print("Changing date")
        # repo.change_repo_date(date)
        print("Date changed")
        json_path = convert_dependency_json_from_repo(repo_name, repo)
        json_list.append(json_path)
        xmi_list.append(convert_json_dependency_to_xmi(repo_name, json_path, repo.local_repo_dir))


    return repo, json_list, xmi_list
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




teku_repo, teku_json_list, teku_xmi_list = create_xmi_from_url("teku", "https://github.com/Consensys/teku")
besu_repo, besu_json_list, besu_xmi_list = create_xmi_from_url("besu", "https://github.com/hyperledger/besu")

for i in range(len(besu_xmi_list)):
    compare(teku_repo, teku_xmi_list[i], besu_repo, besu_xmi_list[i])


# test_url = "https://github.com/ferstl/depgraph-maven-plugin/"
# project_name = "depgraph-maven-plugin"
# repo, json_path = generate_dependency_json(project_name, test_url)
# convert_json_dependency_to_xmi(project_name, json_path)

# petclinic_repo, petclinic_json_path, xmi_path = create_xmi_from_url("PetClinic", "https://github.com/spring-projects/spring-petclinic")