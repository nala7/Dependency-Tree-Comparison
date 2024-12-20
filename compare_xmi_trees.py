import xml.etree.ElementTree as ET


def parse_xmi_projects(xmi_content):
    root = ET.fromstring(xmi_content)
    project_list = []
    project_set = set()

    for project_elem in root.findall(".//depProject"):
        group_id = project_elem.get('groupId', '')
        artifact_id = project_elem.get('artifactId', '')
        # version = project_elem.get('version', '')
        project_list.append((group_id, artifact_id))
        project_set.add((group_id, artifact_id))

    return project_list, project_set


def compare_xmi_files(project_name1, xmi_content1, project_name2, xmi_content2):
    project_list1, project_set1 = parse_xmi_projects(xmi_content1)
    project_list2, project_set2 = parse_xmi_projects(xmi_content2)

    # Find common projects
    print(f"{project_name1} total dependencies: {len(project_list1)}")
    print(f"{project_name2} total dependencies: {len(project_list2)}")
    print('------')
    print(f"{project_name1} set of dependencies: {len(project_set1)}")
    print(f"{project_name2} set of dependencies: {len(project_set2)}")
    print('------')

    common_projects = project_set1.intersection(project_set2)
    print(f"Common projects: {len(common_projects)}")
    for name in common_projects:
        print(name)
    return len(common_projects), common_projects

def compare_trees(project_name1, xmi_file_path1, project_name2, xmi_file_path2):
    with open(xmi_file_path1, 'r', encoding='utf-8') as file1, open(xmi_file_path2, 'r', encoding='utf-8') as file2:
        xmi_content1 = file1.read()
        xmi_content2 = file2.read()
        common_count, common_projects = compare_xmi_files(project_name1, xmi_content1, project_name2, xmi_content2)
        return  common_count, common_projects