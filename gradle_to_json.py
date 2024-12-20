import json
import re

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

# Parse and convert to JSON
parsed_dependencies = parse_gradle_output(input_dependencies)
print(json.dumps(parsed_dependencies, indent=4))
