from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class AnalyzedFileRecord(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    language = Column(String, nullable=False)
    total_lines = Column(Integer)
    code_lines = Column(Integer)

    imports = relationship("ImportRecord", back_populates='file', cascade="all, delete-orphan")
    classes = relationship("ClassRecord", back_populates='file', cascade="all, delete-orphan")
    functions = relationship("FunctionRecord", back_populates='file', cascade="all, delete-orphan")
    calls = relationship("CallRecord", back_populates='file', cascade="all, delete-orphan")


class FunctionRecord(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True)
    global_name = Column(String, unique=True, nullable=False)
    qualified_name = Column(String, nullable=False)
    local_name = Column(String, nullable = False)
    line_start = Column(Integer)
    line_end = Column(Integer)
    source = Column(String)
    return_annotation = Column(String)
    parent_class = Column(String)

    parameters = relationship("ParameterRecord", back_populates='function', cascade='all, delete-orphan')

    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship("AnalyzedFileRecord", back_populates='functions')

    class_id = Column(Integer, ForeignKey('classes.id'))
    containing_class = relationship('ClassRecord', back_populates='methods')

class ParameterRecord(Base):
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    default = Column(String)
    annotation = Column(String)

    function_id = Column(Integer, ForeignKey('functions.id'))
    function = relationship("FunctionRecord", back_populates='parameters')

class ImportRecord(Base):

    __tablename__ = 'imports'

    id = Column(Integer, primary_key=True)
    module = Column(String, nullable=False)
    imported_name = Column(String)
    alias = Column(String)
    line_number = Column(Integer)
    from_import = Column(Boolean, default=False)

    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship("AnalyzedFileRecord", back_populates='imports')

    
    
    
class ClassRecord(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    qualified_name = Column(String, nullable=False)
    global_name = Column(String, nullable=False)
    line_no = Column(Integer)
    bases = Column(JSON, default=list)


    methods = relationship("FunctionRecord", back_populates='containing_class', cascade="all, delete-orphan")

    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship("AnalyzedFileRecord", back_populates='classes')

class CallRecord(Base):

    __tablename__ = "calls"
    id = Column(Integer, primary_key=True)
    qualified_name = Column(String, nullable=False)
    line_number = Column(Integer)
    containing_function = Column(String)

    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship("AnalyzedFileRecord", back_populates='calls')


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///data/db.db")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind = engine)
    session = Session()

    function = FunctionRecord(
        global_name="auth.login.authenticate",
        file_name="auth.py",
        local_name="authenticate",
        line_start=10,
        line_end=15,
        source="def authenticate(username, password): ...",
        return_annotation="bool",
        parent_class=None
    )

    function.parameters = [
        ParameterRecord(
            name="username",
            annotation="str"
        ),
        ParameterRecord(
            name="password",
            annotation="str"
        )
    ]

    session.add(function)
    session.commit()

if __name__ == "__main__":
    main()