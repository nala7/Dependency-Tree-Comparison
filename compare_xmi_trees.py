from lxml import etree

def parse_xmi(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    # namespaces = {'dp': 'geodes.sms.dependencies'}
    namespaces = {'xmi': 'http://www.omg.org/XMI', 'dp': 'geodes.sms.dependencies'}

    # Debugging: Print the root element and its children
    projects = []
    for elem in root.iter():
        if elem.tag == 'depProject':
            group_id = elem.get("groupId")
            artifact_id = elem.get("artifactId")
            version = elem.get("version")
            name = elem.get("name", "Unnamed Project")

            projects.append({
                "name": name,
                "groupId": group_id,
                "artifactId": artifact_id,
                "version": version
            })
    return projects

def find_common_projects(projects1, projects2):
    common_projects = []
    projects1_set = {(p["groupId"], p["artifactId"], p["version"]) for p in projects1}

    for p2 in projects2:
        key = (p2["groupId"], p2["artifactId"], p2["version"])
        if key in projects1_set:
            common_projects.append(p2["name"])

    return common_projects