import os
import subprocess
import xml.etree.ElementTree as ET


def get_project_coordinates(config_file):
    import xml.etree.ElementTree as ET

    root = ET.fromstring(config_file)
    namespaces = {'ns': 'http://maven.apache.org/POM/4.0.0'}

    group_id = root.find('.//ns:groupId', namespaces)
    group_id = group_id.text if group_id is not None else None

    artifact_id = root.find('.//ns:artifactId', namespaces)
    artifact_id = artifact_id.text if artifact_id is not None else None

    if not group_id or not artifact_id:
        raise ValueError("Could not extract project coordinates from pom.xml")

    return f"{group_id}:{artifact_id}"

def add_depgraph_plugin(proj_name, pom_file, file_path):
    namespaces = {'ns': 'http://maven.apache.org/POM/4.0.0'}
    ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')

    # Parse the existing pom.xml content
    root = ET.fromstring(pom_file)

    # Find or create the <build> element
    build_elem = root.find('.//ns:build', namespaces)
    if build_elem is None:
        build_elem = ET.SubElement(root, 'build')

    # Find or create the <plugins> element
    plugins_elem = build_elem.find('.//ns:plugins', namespaces)
    if plugins_elem is None:
        plugins_elem = ET.SubElement(build_elem, 'plugins')

    # Check if the plugin already exists
    existing_plugins = plugins_elem.findall('.//ns:plugin', namespaces)
    for plugin in existing_plugins:
        group_id = plugin.find('ns:groupId', namespaces)
        artifact_id = plugin.find('ns:artifactId', namespaces)

        if (group_id is not None and group_id.text == 'com.github.ferstl' and
                artifact_id is not None and artifact_id.text == 'depgraph-maven-plugin'):
            return pom_file  # Plugin already exists, return original content

    # Create the new plugin element
    plugin_elem = ET.SubElement(plugins_elem, 'plugin')

    # Add groupId
    group_id_elem = ET.SubElement(plugin_elem, 'groupId')
    group_id_elem.text = 'com.github.ferstl'

    # Add artifactId
    artifact_id_elem = ET.SubElement(plugin_elem, 'artifactId')
    artifact_id_elem.text = 'depgraph-maven-plugin'

    # Add version
    version_elem = ET.SubElement(plugin_elem, 'version')
    version_elem.text = '4.0.3'

    # Convert back to string with proper formatting
    from xml.dom import minidom
    import io

    # Convert to string with pretty formatting
    rough_string = ET.tostring(root, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)

    # Use a string writer to get formatted XML
    string_writer = io.StringIO()
    reparsed.writexml(string_writer, addindent="  ", newl="\n", encoding="UTF-8")
    formatted_xml = string_writer.getvalue()

    # Update the config_file with the new content
    pom_file = formatted_xml

    # Optionally, write back to the file if needed
    local_pom_path = os.path.join(file_path, 'pom.xml')
    with open(local_pom_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

    print(f"Depgraph Maven Plugin added to {proj_name}'s pom.xml")

    return formatted_xml

def pom_xml_to_json(project_name, pom_file, file_path):
    res = add_depgraph_plugin(project_name, pom_file, file_path)
    if not res:
        raise ValueError("Failed to add plugin")

    output_file = "dependencies.json"
    dependency_json_path = os.path.join(file_path, output_file)

    original_dir = os.getcwd()
    try:
        os.chdir(file_path)
        # Command to generate dependency graph in JSON format
        project_coordinates = get_project_coordinates(pom_file)
        cmd = f"mvn dependency:tree -DoutputType=json -DoutputFile={output_file}"
        print(cmd)

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Maven command failed: {result.stderr}")
        os.chdir(original_dir)
        if not os.path.exists(dependency_json_path):
            raise FileNotFoundError("Dependency graph JSON was not generated")
        return dependency_json_path

    except Exception as e:
        os.chdir(original_dir)
        raise


def generate_dot_graph(repo):
    if not os.path.exists(repo.local_repo_dir):
        raise FileNotFoundError(f"Local repository directory {repo.local_repo_dir} not found")

    pom_path = os.path.join(repo.local_repo_dir, 'pom.xml')
    if not os.path.exists(pom_path):
        raise FileNotFoundError(f"pom.xml not found in {pom_path}")

    output_file = 'dependency-graph'
    dependency_dot_path = os.path.join(repo.local_repo_dir, output_file)

    original_dir = os.getcwd()


    try:
        os.chdir(repo.local_repo_dir)

        project_coordinates = get_project_coordinates(repo.config_file)
        cmd = f"mvn dependency:tree -DoutputType=dot -DoutputFile={dependency_dot_path}.dot"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        cmd_png = f"mvn dependency:tree -DoutputType=png -DoutputFile={dependency_dot_path}.png"

        result_png = subprocess.run(cmd_png, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Maven command failed: {result.stderr}")

        os.chdir(original_dir)

        if not os.path.exists(dependency_dot_path):
            raise FileNotFoundError("Dependency graph DOT file was not generated")

        repo.graph_generated = True
        return dependency_dot_path

    except Exception as e:
        os.chdir(original_dir)
        raise
