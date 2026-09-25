
from astAnalyzer import PythonASTAnalyzer
from dependencyAnalyzer import DependencyAnalyzer
from data.mappers import analyzed_file_to_record, dependency_to_record, external_dependency_to_record
from data.repository import Database


files = ["astAnalyzer.py","dependencyAnalyzer.py", "models.py"]

analyzed_files = []

for file in files:
    with open(file) as f:
        source = f.read()
    analyzed_files.append(PythonASTAnalyzer(source, file).analyze())


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
print("successfully saved analyzed files")

external_dependency_records = [external_dependency_to_record(dep) for dep in dpna.external_dependencies]
db.save_external_dependencies(external_dependency_records)
print("external dependencies saved successfully")


global_names = dpna.get_entity_endpoint_names()

dependency_records = [dependency_to_record(dep, global_names) for dep in dpna.dependencies]
db.save_dependencies(dependency_records)
print("successfully saved dependency records")


