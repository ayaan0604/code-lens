from models import *
import ast
from pprint import pp


class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, source: str, file_path: str):
        super().__init__()
        self.source = source
        self.file_path = file_path
        self.tree = ast.parse(source)
        self.analyzedFile = AnalyzedFile(None)
        
    #visitor functions
    def visit_Import(self, node):
        for alias in node.names:
            moduleName = alias.name
            importedName = alias.name
            asName = alias.asname
            lineNo = node.lineno

            self.analyzedFile.imports.append(
                ImportInfo(
                    module=moduleName,
                    imported_name = importedName,
                    alias= asName,
                    line_number= lineNo
                )
            )

    def visit_ImportFrom(self, node):
        module = node.module
        line = node.lineno
        for alias in node.names:
            importedName = module + "." + alias.name
            asName = alias.asname  
            self.analyzedFile.imports.append(
                ImportInfo(
                    module= module,
                    imported_name= importedName,
                    alias = asName,
                    line_number=line
                )
            )
                

    #analyzer functions
    def get_metadata(self):
        path = self.file_path
        language = "python" #for now

        lines = self.source.split("\n")

        total_lines = len(lines)

        code_lines = 0

        for line in lines:
            if line.strip().startswith("#") or not line.strip():
                continue

            code_lines+=1

        return Metadata(
            path=path,
            language=language,
            total_lines=total_lines,
            code_lines=code_lines
        )
            
    def getImports(self) -> List[ImportInfo]:
        pass

    def analyze(self) -> AnalyzedFile:

        self.analyzedFile.metadata = self.get_metadata()

        self.visit(self.tree)


        return self.analyzedFile

source = """
import os
from x import y as z

    #this is a comment
 
def hello():
    print("hello")
"""
analyzer = PythonASTAnalyzer(source, "temp.py")
result = analyzer.analyze()

pp(result)