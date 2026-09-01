from models import *
from typing import List


class DependencyAnalyzer():
    def __init__(self, analyzedFiles : List[AnalyzedFile]):

        self.analyzedFiles = analyzedFiles
        self.entity_map = {}
        self.dependencies : List[Dependency] = []

    def get_qualified_file_name(self, filePath: str)-> str:
        file_name = ".".join(filePath.split("/")) #needs to be updated
        
        file_name = file_name.removesuffix(".py") #remove file extension

        return file_name
    #helpers

    def resolve_global_name(self, local_name: str, file: AnalyzedFile):
        filePath = file.metadata.path
        qualified_file_name = self.get_qualified_file_name(filePath)
        #search the current file
        name = qualified_file_name + "." + local_name
        if name in self.entity_map:
            return name 


        #search in the imports
        for imp in file.imports:
            base_name = local_name.split(".")[0]  #in local names like A.B.C, A is the base name
            if base_name == imp.imported_name or base_name==imp.alias:
                
                name = imp.imported_name
                name = imp.module + "." + name if imp.from_import else name

                if name in self.entity_map:
                    return name 
                print(name)

        print("couldn't find ", local_name)
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
                if global_name is not None:
                    target = self.entity_map[global_name]
                    source = cls
                    type = DependencyType.INHERITS
                    line = cls.line_number
                    self.add_dependency(source, target, type, line)

        '''more to be assesed and added'''
        

    def analyze_imports(self, file: AnalyzedFile):

        file_name = self.get_qualified_file_name(file.metadata.path)
    

        for imp in file.imports:
            module = imp.module
            name = imp.imported_name
            line = imp.line_number
            source = file.metadata
            from_import = imp.from_import

            if from_import: #part of module imported
                target_name = module + "." + name
                target = self.entity_map.get(target_name)
                
            else: #whole module imported
                target = self.entity_map.get(module)

            if target is None:
                target = "external dependency" #temporary implementation

            self.dependencies.append(Dependency(
                source=source,
                target=target,
                type= DependencyType.IMPORTS,
                line=line
            ))

    '''to be checked and updated'''

    def analyze_calls(self, file: AnalyzedFile):
        qualified_file_name = self.get_qualified_file_name(file.metadata.path)

        for call in file.calls:
            qname = call.qualified_name

            containing_entity = call.containing_function
            containing_entity = self.resolve_global_name(containing_entity, file) if containing_entity else file.metadata


            line = call.line_number
            source = containing_entity
            target = None
            type = None


            targetName = self.resolve_global_name(qname, file)
            if targetName is None:
                '''external dependency'''
                continue
            target = self.entity_map[targetName]

            if isinstance(target, FunctionInfo):
                type = DependencyType.CALLS
            elif isinstance(target, ClassInfo):
                type = DependencyType.INSTANTIATES

            self.add_dependency(
                source=source,
                target=target,
                type = type,
                line=line
            )
    '''need to implement external libraries'''



    def analyze(self):
        self.populate_entity_map()
        
        for file in self.analyzedFiles:
            self.analyze_imports(file)
            self.analyze_classes(file)
            self.analyze_calls(file)


def main():
    from astAnalyzer import PythonASTAnalyzer
    from pprint import pp

    file1 = 'auth.py'
    with open (file1) as f:
        source1 = f.read()

    file2 = 'services.py'
    with open(file2) as f:
        source2 = f.read()


    pythonAnalyzer1 = PythonASTAnalyzer(source1, file1)
    pythonAnalyzer2 = PythonASTAnalyzer(source2, file2)
    result1 = pythonAnalyzer1.analyze()
    result2 = pythonAnalyzer2.analyze()

    dependencyAnalyzer = DependencyAnalyzer([result1, result2])
    dependencyAnalyzer.populate_entity_map()

    #pp(dependencyAnalyzer.entity_map)
    # pp(result1.calls)
    # dependencyAnalyzer.analyze()
    # pp(dependencyAnalyzer.dependencies)

    print(dependencyAnalyzer.resolve_global_name("authenticate", result1) )
    print(dependencyAnalyzer.resolve_global_name("UserService", result1) )
    print(dependencyAnalyzer.resolve_global_name("UserService.login", result1) )

if __name__ == "__main__":
    main()