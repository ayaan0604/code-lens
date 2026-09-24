from astAnalyzer import PythonASTAnalyzer
from dependencyAnalyzer import DependencyAnalyzer
from data.mappers import analyzed_file_to_record
from data.repository import Database

file1 = "astAnalyzer.py"
file2 = "dependencyAnalyzer.py"
with open(file1) as f:
    source1 = f.read()
with open(file2) as f:
    source2 = f.read()

ast1  = PythonASTAnalyzer(source1, file1)
ast2  = PythonASTAnalyzer(source2, file2)

analyzed_files = [ast1.analyze(), ast2.analyze()]

dpna = DependencyAnalyzer(analyzed_files)
dpna.analyze()

global_names = [dpna.get_file_global_names(file = file) for file in analyzed_files]

records = [
    analyzed_file_to_record(analyzed_files[i], global_names[i])
    for i in range(len(analyzed_files))
]

db = Database()
db.base.metadata.drop_all(bind = db.engine)
db.base.metadata.create_all(bind = db.engine)

db.save_many_analyzed_file_records(records)
print("success")

