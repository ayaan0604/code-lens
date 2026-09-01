from models import *
import ast
from pprint import pp
from typing import List, Union

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, source: str, file_path: str):
        super().__init__()
        self.source = source
        self.file_path = file_path
        self.tree = ast.parse(source)
        self.analyzedFile = None
        
        self.scope : List[Union[ClassInfo, FunctionInfo]]= []


    #helper functions
    def get_current_scope_name(self)->str:
        return ".".join([node.name for node in self.scope])

    def get_current_class(self) -> ClassInfo | None:
        for item in reversed(self.scope):
            if isinstance(item, ClassInfo):
                return item
        else:
            return None

    def get_current_function(self)-> FunctionInfo | None:
        for item in reversed(self.scope):
            if isinstance(item, FunctionInfo):
                return item
        else:
            return None
        
    def get_current_scope(self)-> ClassInfo | FunctionInfo | None:
        return self.scope[-1] if self.scope else None

    def getParameters(self, args: ast.arguments)->List[ParameterInfo]:
            parameters :List[ParameterInfo] = []
            for arg in args.args:
                pname = arg.arg
                pann = None if arg.annotation is None else ast.unparse(arg.annotation) 
                default = None
                parameters.append(ParameterInfo(pname, default, pann))
    
            idx = 1
            for default in reversed(args.defaults):
                parameters[-idx].default = ast.unparse(default) if default is not None else default
                idx+=1
    
            return parameters

    def getFunctionInfo(self, node)-> FunctionInfo:
        name = node.name
        lineStart = node.lineno
        lineEnd = node.end_lineno
        sourceCode = ast.get_source_segment(self.source, node)
        
        parameters = self.getParameters(node.args)

        current_scope_name = self.get_current_scope_name()
        if not current_scope_name:
            qualified_name = name
        else:
            qualified_name = ".".join([current_scope_name] + [name])

        parent = self.get_current_scope()
        parent = parent.qualified_name if parent else None

        returnaAnnotation = ast.unparse(node.returns) if node.returns else None

        return FunctionInfo(
            name,
            qualified_name,
            lineStart,
            lineEnd,
            sourceCode,
            parent,
            returnaAnnotation,
            parameters
        )


    def getClassInfo(self, node:ast.ClassDef) -> ClassInfo:
        name = node.name

        current_scope_name = self.get_current_scope_name()
        if not current_scope_name:
            qualified_name = name
        else:
            qualified_name = ".".join([current_scope_name] + [name])


        lineNumber = node.lineno

        bases = [ast.unparse(b) for b in node.bases]

        methods = []

        return ClassInfo(
            name = name,
            qualified_name= qualified_name,
            line_number=lineNumber,
            bases= bases,
            methods= methods
        )

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

    def get_qualified_call_name(self, node):
        if isinstance(node, ast.Call):
                    return self.get_qualified_call_name(node.func)
        
        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.Attribute):
            return self.get_qualified_call_name(node.value) + "." + node.attr


    def get_call_info(self, node)-> CallInfo:
        qname = self.get_qualified_call_name(node) 
        lineno = node.lineno
        containing_func = self.get_current_scope_name()

        return CallInfo(
            qualified_name = qname,
            line_number= lineno,
            containing_function= containing_func if containing_func else None
        )
        
    
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
                    line_number=line,
                    from_import=True
                )
            )

    

    def visit_FunctionDef(self, node):
        
        function_info = self.getFunctionInfo(node)

        
        

        self.analyzedFile.functions.append(function_info)

        parent = self.get_current_scope()
        if parent is not None and isinstance(parent, ClassInfo):
            parent.methods.append(function_info)

        self.scope.append(function_info)

        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):

        info = self.getClassInfo(node)


        self.analyzedFile.classes.append(info)

        self.scope.append(info)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Call(self, node):
        info = self.get_call_info(node)
        self.analyzedFile.calls.append(info)
        self.generic_visit(node)
        
    #analyzer functions
    
            

    def analyze(self) -> AnalyzedFile:

        self.analyzedFile = AnalyzedFile(metadata=self.get_metadata())

        self.visit(self.tree)


        return self.analyzedFile

def main():

    source = """
from x import y
class A:

    def foo(self):

        def inner():
            authenticate()

        inner()


class B:

    def foo(self):
        something.run()
y.z()
    """
    analyzer = PythonASTAnalyzer(source, "temp.py")
    result = analyzer.analyze()
    from dataclasses import asdict
    
    pp(result)
    import sys
    print(sys.getsizeof(result))

if __name__ == "__main__":
    main()