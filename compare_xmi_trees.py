from lxml import etree


def parse_xmi(file_path):
    """
    Parses an XMI file and extracts all projects with their attributes.
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Extract namespaces
    namespaces = {'dp': 'geodes.sms.dependencies'}

    # Find all Project elements
    projects = []
    for project in root.findall(".//dp:Project", namespaces):
        group_id = project.find("dp:groupId", namespaces).text
        artifact_id = project.find("dp:artifactId", namespaces).text
        version = project.find("dp:version", namespaces).text
        name = project.get("name", "Unnamed Project")

        projects.append({
            "name": name,
            "groupId": group_id,
            "artifactId": artifact_id,
            "version": version
        })
    return projects


def find_common_projects(projects1, projects2):
    """
    Finds common projects between two lists of projects.
    """
    common_projects = []
    projects1_set = {(p["groupId"], p["artifactId"], p["version"]) for p in projects1}

    for p2 in projects2:
        key = (p2["groupId"], p2["artifactId"], p2["version"])
        if key in projects1_set:
            common_projects.append(p2["name"])

    return common_projects



