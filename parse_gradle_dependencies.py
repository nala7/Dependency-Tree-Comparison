import json
import subprocess
import re
import os


def run_gradle_dependencies(file_path):
    try:
        os.chdir(file_path)
        result = subprocess.run(
            ["./gradlew", "dependencies"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("Error running gradle dependencies:", result.stderr)
            return None
        return result.stdout
    except FileNotFoundError:
        print("Gradle is not installed or not found in PATH.")
        return None

def parse_dependency_line(line):
    match = re.match(r'\\--- (.*?):(.*?):(.*?)$', line.strip())
    if match:
        group_id, artifact_id, version = match.groups()
        return {
            "groupId": group_id,
            "artifactId": artifact_id,
            "version": version,
            "type": "jar",
            "scope": "",
            "classifier": "",
            "optional": "false",
            "children": []
        }
    return None

def parse_dependencies(lines, level=0):
    result = []
    while lines:
        line = lines[0]
        current_level = len(re.match(r"(\s*)", line).group(1)) // 4
        if current_level < level:
            break
        if current_level > level:
            children = parse_dependencies(lines, level + 1)
            if result:
                result[-1]["children"].extend(children)
            continue
        lines.pop(0)
        match = re.match(r"\s*\+--- ([^:]+):([^:]+):([^ ]+)", line)
        if not match:
            match = re.match(r"\s*\\--- ([^:]+):([^:]+):([^ ]+)", line)
        if match:
            group_id, artifact_id, version = match.groups()
            result.append({
                "groupId": group_id,
                "artifactId": artifact_id,
                "version": version,
                "children": []
            })
    return result

def parse_gradle_output(input_text):
    lines = input_text.strip().split("\n")
    dependencies = {
        "groupId": "java-gradle-starter-project",
        "artifactId": "my-app",
        "version": "1.0-SNAPSHOT",
        "children": []
    }
    for i, line in enumerate(lines):
        if line.startswith("compileClasspath"):
            dependencies["children"] = parse_dependencies(lines[i + 1:])
            break
    return dependencies

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    return filename


def gradle_to_json(file_path):
    output = run_gradle_dependencies(file_path)
    if output:
        parsed_dependencies = parse_gradle_output(output)
        json_path = save_to_json(parsed_dependencies, "dependencies.json")
        print("Dependencies have been saved to dependencies.json.")
        return json_path
