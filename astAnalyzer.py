from models import *
import ast


class PythonASTAnalyzer:
    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.tree = ast.parse(source)

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

        metadata = self.get_metadata()


        return AnalyzedFile(
            metadata
        )

source = """
import os

    #this is a comment
 
def hello():
    print("hello")
"""
analyzer = ASTAnalyzer(source, "temp.py")
result = analyzer.analyze()

print(result)