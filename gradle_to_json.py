import os
import subprocess
import json


build_gradle_path = "build.gradle"

gradle_script = """
import groovy.json.JsonBuilder

task generateDependencyHierarchyJson {
    doLast {
        def rootDependencies = [:]

        configurations.findAll { it.isCanBeResolved() }.each { configuration ->
            try {
                def configDependencies = []

                configuration.resolvedConfiguration.firstLevelModuleDependencies.each { dependency ->
                    configDependencies << buildDependencyTree(dependency)
                }

                if (!configDependencies.isEmpty()) {
                    rootDependencies[configuration.name] = configDependencies
                }
            } catch (Exception e) {
                println "Could not resolve dependencies for configuration: ${configuration.name}"
                println "Error: ${e.message}"
            }
        }

        def jsonOutput = new JsonBuilder(rootDependencies).toPrettyString()
        new File("${buildDir}/dependency-hierarchy.json").write(jsonOutput)
    }
}

def buildDependencyTree(dependency) {
    def dependencyNode = [
        group: dependency.moduleGroup,
        name: dependency.moduleName,
        version: dependency.moduleVersion,
        children: []
    ]

    dependency.children.each { childDependency ->
        dependencyNode.children << buildDependencyTree(childDependency)
    }

    return dependencyNode
}
"""


def append_to_build_gradle(file_path, script):
    local_gradle_path = os.path.join(file_path, 'build.gradle')

    try:
        with open(local_gradle_path, "a") as file:
            file.write("\n" + script.strip() + "\n")
        print(f"Groovy script successfully appended to {local_gradle_path}")
    except FileNotFoundError:
        print(f"Error: {local_gradle_path} not found. Please ensure the file exists.")


def run_gradle_task(file_path):
    print("Running Gradle task to generate dependency-hierarchy.json...")
    try:
        os.chdir(file_path)
        subprocess.run(["./gradlew", "buildDependencyTree"], check=True)
        print("Gradle task completed successfully!")
    except subprocess.CalledProcessError:
        print("Error running Gradle task. Please check your build.gradle file.")
        exit(1)


def find_dependency_json(file_path):
    json_path = os.path.join(file_path, "dependency-hierarchy.json")
    if os.path.exists(json_path):
        print(f"JSON file found at: {json_path}")
        return json_path
    else:
        print("Error: dependency-hierarchy.json not found in build directory.")
        exit(1)


def read_json(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
        print("\nGenerated Dependency Hierarchy JSON:")
        print(json.dumps(data, indent=4))


def generate_json_from_gradle(project_name, gradle_file, file_path):
    append_to_build_gradle(file_path, gradle_script)
    run_gradle_task(file_path)
    json_path = find_dependency_json(file_path)
    read_json(json_path)
    return json_path
