
from astAnalyzer import PythonASTAnalyzer
from dependencyAnalyzer import DependencyAnalyzer
from data.mappers import analyzed_file_to_record, dependency_to_record, external_dependency_to_record, dependency_record_to_dependency
from data.repository import Database
from data.models import DependencyRecord
from models import DependencyType


files = ["astAnalyzer.py","dependencyAnalyzer.py", "models.py"]

analyzed_files = []

for file in files:
    with open(file) as f:
        source = f.read()
    analyzed_files.append(PythonASTAnalyzer(source, file).analyze())


dpna = DependencyAnalyzer(analyzed_files)
dpna.analyze()

global_names1 = dpna.get_entity_endpoint_names()

records = [
    analyzed_file_to_record(file, dpna.get_file_global_names(file))
    for file in analyzed_files
    
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

with db.Session() as session:

    records = session.query(DependencyRecord).all()

    for record in records:

        dependency = dependency_record_to_dependency(
            record,
            db.get_entity
        )

        print("\nDependency:")
        print("  Source:", dependency.source)
        print("  Target:", dependency.target)
        print("  Type:", dependency.type)
        print("  Line:", dependency.line)

    record = records[0]

    dependency = dependency_record_to_dependency(
        record,
        db.get_entity
    )

    assert dependency is not None
    assert dependency.type == DependencyType(record.type)
    assert dependency.line == record.line_no

    print("Dependency round-trip passed!")

print("\nDependency retrieval passed!")
