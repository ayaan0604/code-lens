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
        self.scope = []
        
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
            importedName = alias.name
            asName = alias.asname  
            self.analyzedFile.imports.append(
                ImportInfo(
                    module= module,
                    imported_name= importedName,
                    alias = asName,
                    line_number=line
                )
            )

    def getParameters(self, args: ast.arguments)->List[ParameterInfo]:
        parameters :List[ParameterInfo] = []
        for arg in args.args:
            pname = arg.arg
            pann = None if arg.annotation is None else ast.unparse(arg.annotation) 
            default = None
            parameters.append(ParameterInfo(pname, default, pann))

        idx = 1
        for default in args.defaults:
            parameters[-idx].default = ast.unparse(default) if default is not None else default
            idx+=1

        return parameters

    def visit_FunctionDef(self, node):
        name = node.name
        lineStart = node.lineno
        lineEnd = node.end_lineno
        sourceCode = ast.get_source_segment(self.source, node)
        
        parameters = self.getParameters(node.args)

        qualified_name = ".".join(self.scope + [name])

        parent = self.scope[-1] if self.scope else None


        returnaAnnotation = node.returns.id if node.returns else None

        self.analyzedFile.functions.append(
            FunctionInfo(
                name,
                qualified_name,
                lineStart,
                lineEnd,
                sourceCode,
                parent,
                returnaAnnotation,
                parameters
            )
        )

        self.generic_visit(node)
        
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
            

    def analyze(self) -> AnalyzedFile:

        self.analyzedFile.metadata = self.get_metadata()

        self.visit(self.tree)


        return self.analyzedFile

source = """
import os
from x import y as z

    #this is a comment
 
def hello(name:Optional[str], x=10, y=20)->str:
    print("hello")
    return name
"""
analyzer = PythonASTAnalyzer(source, "temp.py")
result = analyzer.analyze()

pp(result)