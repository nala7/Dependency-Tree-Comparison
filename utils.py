import re
import subprocess
import os


def from_gradle_to_pom_xml(self):
    if not self.is_gradle:
        raise Exception("This repository does not have a build.gradle file.")

        # Clone the repository locally
    if not os.path.exists(self.local_repo_dir):
        subprocess.run(["git", "clone", self.url_path, self.local_repo_dir], check=True)

    # Add Maven publishing to build.gradle
    gradle_file_path = os.path.join(self.local_repo_dir, "build.gradle")
    add_maven_publishing(gradle_file_path)

    # Run Gradle task to generate POM file
    result = subprocess.run(
        ["./gradlew", "generatePomFileForMavenJavaPublication"],
        cwd=self.local_repo_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to run Gradle task: {result.stderr}")

    # Locate and read the generated POM file
    pom_file_path = os.path.join(self.local_repo_dir, "build", "publications", "mavenJava", "pom-default.xml")
    if not os.path.exists(pom_file_path):
        raise Exception("POM file was not generated.")

    with open(pom_file_path, "r") as pom_file:
        pom_content = pom_file.read()
        print("Generated POM file content:\n")
        print(pom_content)
        return pom_content

def add_maven_publishing(gradle_file_path):
    # Check if the file exists
    if not os.path.exists(gradle_file_path):
        raise FileNotFoundError(f"The file {gradle_file_path} does not exist.")

    # Read the file content
    with open(gradle_file_path, "r") as gradle_file:
        gradle_content = gradle_file.read()

    # Add maven-publish plugin if not present
    if not re.search(r'plugins\s*{[^}]*id\s*[\'"]maven-publish[\'"]\s*', gradle_content, re.DOTALL):
        gradle_content = re.sub(
            r'(plugins\s*{)',
            r'\1\n    id \'maven-publish\'',
            gradle_content
        ) if 'plugins {' in gradle_content else f"plugins {{\n    id 'maven-publish'\n}}\n{gradle_content}"

    # Add publishing block if not present
    if 'publishing {' not in gradle_content:
        gradle_content += """
publishing {
    publications {
        mavenJava(MavenPublication) {
            from components.java
        }
    }
}
"""
    else:
        # Ensure mavenJava publication exists within publishing block
        publishing_match = re.search(r'(publishing\s*{[^}]*publications\s*{)([^}]*)}', gradle_content, re.DOTALL)
        if publishing_match:
            publications_block = publishing_match.group(2)
            if 'mavenJava(MavenPublication)' not in publications_block:
                gradle_content = gradle_content.replace(
                    publishing_match.group(0),
                    f"{publishing_match.group(1)}{publications_block}\n        mavenJava(MavenPublication) {{\n            from components.java\n        }}\n    }}"
                )

    # Write the updated content back to the file
    with open(gradle_file_path, "w") as gradle_file:
        gradle_file.write(gradle_content)