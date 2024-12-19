from dataclasses import dataclass, field
from typing import List, Optional
import xml.etree.ElementTree as ET


@dataclass
class Dependency:
    name: str
    methods: List[str] = field(default_factory=list)
    dep_project: List['Project'] = field(default_factory=list)


@dataclass
class Project:
    name: str
    group_id: str
    artifact_id: str
    version: str
    dependencies: List[Dependency] = field(default_factory=list)


@dataclass
class DependencyTree:
    name: str
    projects: List[Project] = field(default_factory=list)


@dataclass
class DependencyForest:
    dependency_trees: List[DependencyTree] = field(default_factory=list)


class JsonToXmiConverter:
    @staticmethod
    def convert_json_to_xmi(json_data):
        # Create dependency forest
        forest = DependencyForest()
        tree = DependencyTree(name="RootDependencyTree")

        # Create root project
        root_project = JsonToXmiConverter._create_project(json_data)
        tree.projects.append(root_project)

        forest.dependency_trees.append(tree)

        # Convert to XMI
        return JsonToXmiConverter._to_xmi(forest)

    @staticmethod
    def _create_project(project_data):
        project = Project(
            name=project_data.get('artifactId', ''),
            group_id=project_data.get('groupId', ''),
            artifact_id=project_data.get('artifactId', ''),
            version=project_data.get('version', '')
        )

        if 'children' in project_data:
            for child in project_data['children']:
                dependency = Dependency(
                    name=child.get('artifactId', ''),
                    dep_project=[JsonToXmiConverter._create_project(child)]
                )
                project.dependencies.append(dependency)

        return project

    @staticmethod
    def _to_xmi(forest):
        # Create XMI root
        root = ET.Element('xmi:XMI', {
            'xmlns:xmi': 'http://www.omg.org/XMI',
            'xmlns:dp': 'geodes.sms.dependencies'
        })

        forest_elem = ET.SubElement(root, 'dp:DependencyForest')

        def add_project_dependencies(project_element, project):
            for dep in project.dependencies:
                dep_elem = ET.SubElement(project_element, 'dependencies')
                dep_elem.set('xmi:type', 'dp:Dependency')
                dep_elem.set('name', dep.name)

                # for method in dep.methods:
                #     method_elem = ET.SubElement(dep_elem, 'methods')
                #     method_elem.text = method

                if dep.dep_project:
                    for dependency_project in dep.dep_project:
                        dep_project_elem = ET.SubElement(dep_elem, 'depProject')
                        dep_project_elem.set('xmi:type', 'dp:Project')
                        dep_project_elem.set('name', dependency_project.name)
                        dep_project_elem.set('groupId', dependency_project.group_id)
                        dep_project_elem.set('artifactId', dependency_project.artifact_id)
                        dep_project_elem.set('version', dependency_project.version)

                        add_project_dependencies(dep_project_elem, dependency_project)

        for tree in forest.dependency_trees:
            tree_elem = ET.SubElement(forest_elem, 'dependencyTrees')
            tree_elem.set('xmi:type', 'dp:DependencyTree')
            tree_elem.set('name', tree.name)

            for project in tree.projects:
                proj_elem = ET.SubElement(tree_elem, 'projects')
                proj_elem.set('xmi:type', 'dp:Project')
                proj_elem.set('name', project.name)
                proj_elem.set('groupId', project.group_id)
                proj_elem.set('artifactId', project.artifact_id)
                proj_elem.set('version', project.version)

                add_project_dependencies(proj_elem, project)

        return ET.tostring(root, encoding='unicode')

