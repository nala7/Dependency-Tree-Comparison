from lxml import etree
import xml.etree.ElementTree as ET


def parse_dependency(element, namespace):
    project = {
        "name": element.attrib.get("name"),
        "groupId": element.attrib.get("groupId"),
        "artifactId": element.attrib.get("artifactId"),
        "version": element.attrib.get("version"),
        "dependencies": []
    }
    for dependency in element.findall(".//dp:dependencies", namespace):
        dep_project = dependency.find("dp:Project", namespace)
        if dep_project is not None:
            project["dependencies"].append(parse_dependency(dep_project, namespace))
    return project

def parse_xmi(xmi_data):
    root = ET.fromstring(xmi_data)
    namespace = {'xmi': 'http://www.omg.org/XMI', 'dp': 'geodes.sms.dependencies'}
    root_project = root.find(".//dp:Project", namespace)
    parsed_project = parse_dependency(root_project, namespace)
    return parsed_project

    # tree = etree.parse(xmi_data)
    # root = tree.getroot()
    #
    # # namespaces = {'dp': 'geodes.sms.dependencies'}
    # namespaces = {'xmi': 'http://www.omg.org/XMI', 'dp': 'geodes.sms.dependencies'}
    #
    # # Debugging: Print the root element and its children
    # projects = []
    # for elem in root.iter():
    #     if elem.tag == 'depProject':
    #         group_id = elem.get("groupId")
    #         artifact_id = elem.get("artifactId")
    #         version = elem.get("version")
    #         name = elem.get("name", "Unnamed Project")
    #
    #         projects.append({
    #             "name": name,
    #             "groupId": group_id,
    #             "artifactId": artifact_id,
    #             "version": version
    #         })
    # return projects

def find_common_projects(projects1, projects2):
    common_projects = []
    projects1_set = {(p["groupId"], p["artifactId"], p["version"]) for p in projects1}

    for p2 in projects2:
        key = (p2["groupId"], p2["artifactId"], p2["version"])
        if key in projects1_set:
            common_projects.append(p2["name"])

    return common_projects