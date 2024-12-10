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

        # Process children
        if 'children' in json_data:
            for child in json_data['children']:
                child_project = JsonToXmiConverter._create_project(child)
                tree.projects.append(child_project)

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
            'xmlns:dp': 'geodes.sms.dependency'
        })

        # Create DependencyForest
        forest_elem = ET.SubElement(root, 'dp:DependencyForest')

        # Create DependencyTree
        for tree in forest.dependency_trees:
            tree_elem = ET.SubElement(forest_elem, 'dependencyTrees')
            tree_elem.set('xmi:type', 'dp:DependencyTree')
            tree_elem.set('name', tree.name)

            # Create Projects
            for project in tree.projects:
                proj_elem = ET.SubElement(tree_elem, 'projects')
                proj_elem.set('xmi:type', 'dp:Project')
                proj_elem.set('name', project.name)
                proj_elem.set('groupId', project.group_id)
                proj_elem.set('artifactId', project.artifact_id)
                proj_elem.set('version', project.version)

                # Create Dependencies
                for dep in project.dependencies:
                    dep_elem = ET.SubElement(proj_elem, 'dependencies')
                    dep_elem.set('xmi:type', 'dp:Dependency')
                    dep_elem.set('name', dep.name)

        return ET.tostring(root, encoding='unicode')
