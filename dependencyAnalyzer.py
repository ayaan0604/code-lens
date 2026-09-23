from models import *
from typing import List
from pathlib import Path


class DependencyAnalyzer():
    def __init__(self, analyzedFiles : List[AnalyzedFile]):

        self.analyzedFiles = analyzedFiles
        self.entity_map = {}
        self.dependencies : List[Dependency] = []

    def get_qualified_file_name(self, filePath: str)-> str:
        path = Path(filePath)
        return ".".join(path.with_suffix("").parts)  #remove .py from suffix
        

        
    #helpers

    def resolve_global_name(self, local_name: str, file: AnalyzedFile) -> str | None:
        '''
            this function returns the fully qualified global level name,
            global name like filename.class.attr... etc
            for external dependencies, global name is their raw qualified name
            the recieving function should now decide what to do with it
        '''
        
        filePath = file.metadata.path
        qualified_file_name = self.get_qualified_file_name(filePath)
        #search the current file
        name = qualified_file_name + "." + local_name
        if name in self.entity_map:
            return name 


        #search for external dependency
        # if local_name in self.entity_map:
        #     return local_name

        #search in the imports
        base_name = local_name.split(".")[0]  #in local names like A.B.C, A is the base name
        for imp in file.imports:
            if base_name != imp.imported_name and base_name!=imp.alias:
                continue

            if imp.from_import:
                global_name = imp.module + '.' + imp.imported_name
                remaining = local_name.split(".")[1:]
                if remaining:
                    global_name += "." + ".".join(remaining)

            else:
                remaining = local_name.split(".")[1:]

                global_name = imp.module 

                if remaining:
                    global_name+= "." + ".".join(remaining)

            
            return global_name
        

        #print("couldn't find ", local_name)
        return None
        

    def add_dependency(self, source, target, type, line):
        self.dependencies.append(
            Dependency(
                source= source,
                target= target,
                type = type,
                line=line
            )
        )

    def add_external_dependency(self, module, name):

        if name in self.entity_map:
            return self.entity_map[name]

        extdep = ExternalDependency(
                        module= module,
                        name = name
                    )
        self.entity_map[name] = extdep

        return extdep

    def replace_base_name(self, full_name, new_base):
        """replaces the base of a qualified name, used when replacing base with alias"""
        nameList = full_name.split(".")
        nameList[0] = new_base
        return ".".join(nameList)

    def add_to_entity_map(self, file:AnalyzedFile):
        file_name = self.get_qualified_file_name(file.metadata.path)

        for functionInfo in file.functions:
            qname = file_name + "." + functionInfo.qualified_name
            self.entity_map[qname] = functionInfo

        for classInfo in file.classes:
            qname = file_name + "." + classInfo.qualified_name
            self.entity_map[qname] = classInfo
    

    def populate_entity_map(self):
        for file in self.analyzedFiles:
            self.add_to_entity_map(file)
    #analyzing functions

    def analyze_classes(self, file: AnalyzedFile):
        file_name = self.get_qualified_file_name(file.metadata.path)

        #add bases as dependencies
        for cls in file.classes:
            for base in cls.bases:
                global_name = self.resolve_global_name(base, file)
                if global_name is None:
                    continue

                target = self.entity_map.get(global_name)
                if target is None:
                    continue

                source = cls
                type = DependencyType.INHERITS
                line = cls.line_number
                self.add_dependency(source, target, type, line)

        '''more to be assesed and added'''
        

    def analyze_imports(self, file: AnalyzedFile):
    

        for imp in file.imports:
            module = imp.module
            name = imp.imported_name
            line = imp.line_number
            source = file.metadata
            from_import = imp.from_import

            if from_import: #part of module imported
                target_name = module + "." + name
                target = self.entity_map.get(target_name)
                if target is None:
                    #external dependency (from import)
                    target = self.add_external_dependency(module=module, name = target_name)
                
            else: #whole module imported
                target = self.entity_map.get(module)

                if target is None:
                    #external dependency (whole import)
                    target = self.add_external_dependency(module = module, name = name)
                    

            self.add_dependency(
                source=source,
                target=target,
                type= DependencyType.IMPORTS,
                line=line
            )

    '''to be checked and updated'''

    def analyze_calls(self, file: AnalyzedFile):
        for call in file.calls:
            qname = call.qualified_name

            if call.containing_function:
                source_name = self.resolve_global_name(
                    call.containing_function,
                    file
                )

                source = (
                    self.entity_map.get(source_name)
                    if source_name
                    else file.metadata
                )
            else:
                source = file.metadata

            target_name = self.resolve_global_name(qname, file)

            if target_name is None:
                '''target is not recognised'''
                continue

            target = self.entity_map.get(target_name)

            if target is None:
                '''this step will add the arbitrary name as an external dependency.
                an improvement would be to check if the base entity is really a recognised dependency '''
                                    
                base_name = target_name.split(".")[0]

                target = self.add_external_dependency(
                    module=base_name,
                    name=target_name
                )
                
    
                    

            if target is None:
                continue

            if isinstance(target, ClassInfo):
                dependency_type = DependencyType.INSTANTIATES
            else:
                dependency_type = DependencyType.CALLS

            self.add_dependency(
                source=source,
                target=target,
                type=dependency_type,
                line=call.line_number
            )

   

    def analyze(self):
        self.populate_entity_map()
        
        for file in self.analyzedFiles:
            self.analyze_imports(file)
            self.analyze_classes(file)
            self.analyze_calls(file)


def main():
    from astAnalyzer import PythonASTAnalyzer
    from pprint import pp

    file1 = 'astAnalyzer.py'
    with open (file1) as f:
        source1 = f.read()

    


    pythonAnalyzer1 = PythonASTAnalyzer(source1, file1)
    result1 = pythonAnalyzer1.analyze()


    dependencyAnalyzer1 = DependencyAnalyzer([result1])
    dependencyAnalyzer1.analyze()

   
    pp(dependencyAnalyzer1.dependencies)
    pp(dependencyAnalyzer1.entity_map.keys())

    # print(dependencyAnalyzer.resolve_global_name("auth.authenticate", result1) )
    # print(dependencyAnalyzer.resolve_global_name("a.authenticate", result1) )
    # print(dependencyAnalyzer.resolve_global_name("authenticate", result1) )
    # print(dependencyAnalyzer.resolve_global_name("US", result1) )



def test():
    """test code written by chatgpt"""
    from astAnalyzer import PythonASTAnalyzer
    from pprint import pp

    source = """
import requests
from math import sqrt


class Base:
    pass


class Child(Base):
    pass


def authenticate():
    pass


def login():
    authenticate()
    requests.get("https://example.com")
    sqrt(25)


def main_function():
    Child()
    login()
"""

    file_path = "test.py"

    analyzer = PythonASTAnalyzer(source, file_path)
    analyzed_file = analyzer.analyze()

    dependency_analyzer = DependencyAnalyzer([analyzed_file])
    dependency_analyzer.analyze()

    print("\n========== ENTITY MAP ==========")
    pp(dependency_analyzer.entity_map)

    print("\n========== DEPENDENCIES ==========")
    for dependency in dependency_analyzer.dependencies:
        source_name = getattr(
            dependency.source,
            "qualified_name",
            getattr(dependency.source, "path", str(dependency.source))
        )

        target_name = getattr(
            dependency.target,
            "qualified_name",
            getattr(dependency.target, "name", str(dependency.target))
        )

        print(
            f"{source_name} "
            f"--[{dependency.type.value}]--> "
            f"{target_name}"
        )

    print("\n========== RESOLVER TESTS ==========")

    test_names = [
        "authenticate",
        "Child",
        "Base",
        "requests.get",
        "sqrt",
    ]

    for name in test_names:
        result = dependency_analyzer.resolve_global_name(
            name,
            analyzed_file
        )

        print(f"{name:20} -> {result}")

    print("\n========== BASIC CHECKS ==========")

    entity_map = dependency_analyzer.entity_map
    dependencies = dependency_analyzer.dependencies

    assert "test.authenticate" in entity_map
    assert "test.login" in entity_map
    assert "test.Child" in entity_map
    assert "test.Base" in entity_map

    assert any(
        dependency.type == DependencyType.INHERITS
        for dependency in dependencies
    )

    assert any(
        dependency.type == DependencyType.INSTANTIATES
        for dependency in dependencies
    )

    assert any(
        dependency.type == DependencyType.CALLS
        for dependency in dependencies
    )

    assert any(
        dependency.type == DependencyType.IMPORTS
        for dependency in dependencies
    )

    assert (
        dependency_analyzer.resolve_global_name(
            "authenticate",
            analyzed_file
        ) == "test.authenticate"
    )

    assert (
        dependency_analyzer.resolve_global_name(
            "Child",
            analyzed_file
        ) == "test.Child"
    )

    assert (
        dependency_analyzer.resolve_global_name(
            "requests.get",
            analyzed_file
        ) == "requests.get"
    )

    assert (
        dependency_analyzer.resolve_global_name(
            "sqrt",
            analyzed_file
        ) == "math.sqrt"
    )

    print("\n✅ ALL BASIC CHECKS PASSED")
    


if __name__ == "__main__":
    main()