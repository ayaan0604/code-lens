from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class AnalyzedFileRecord(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)

    functions = relationship("FunctionRecord", back_populates='file')


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
    file_id = Column(Integer, ForeignKey('files.id'))

    parameters = relationship("ParameterRecord", back_populates='function')
    file = relationship("AnalyzedFileRecord", back_populates='functions')

class ParameterRecord(Base):
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    default = Column(String)
    annotation = Column(String)

    function_id = Column(Integer, ForeignKey('functions.id'))

    function = relationship("FunctionRecord", back_populates='parameters')



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