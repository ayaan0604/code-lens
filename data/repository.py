from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, selectinload
from .models import AnalyzedFileRecord, FunctionRecord, ClassRecord
from typing import List

class Database :
    def __init__(self, db_path: str, base: DeclarativeBase):
        self.db_path = db_path
        self.base = base

        self.engine = create_engine(db_path)
        self.base.metadata.create_all(self.engine)

        self.Session = sessionmaker( bind = self.engine)

    def _analysed_file_retrieval_options(self):
        return [
            selectinload(AnalyzedFileRecord.imports),

            selectinload(AnalyzedFileRecord.functions)
            .selectinload(FunctionRecord.parameters),

            selectinload(AnalyzedFileRecord.classes)
            .selectinload(ClassRecord.methods),

            selectinload(AnalyzedFileRecord.calls)
        ]

    def save_analyzed_file_record(self, record: AnalyzedFileRecord):
        with self.Session() as session:
            session.add(record)
            session.commit()

    def save_many_analyzed_file_records(self, records: List[AnalyzedFileRecord]):
        if not records:
            return
        
        with self.Session() as session:
            session.add_all(records)
            session.commit()


    def get_analyzed_file_record(self, id):
        with self.Session() as session:
            stmt = select(AnalyzedFileRecord).options(
                *self._analysed_file_retrieval_options()
           ).where(AnalyzedFileRecord.id == id)

            result = session.execute(stmt)

            return result.scalar_one_or_none()


    def get_analyzed_file_by_path(self, path: str):
        with self.Session() as session:
            stmt = select(AnalyzedFileRecord).options(
                *self._analysed_file_retrieval_options()
           ).where(AnalyzedFileRecord.path == path)

            result = session.execute(stmt)

            return result.scalar_one_or_none()

        
    def get_all_analyzed_files(self):
        with self.Session() as session:
            stmt = select(AnalyzedFileRecord).options(
                *self._analysed_file_retrieval_options()
            )

            result = session.execute(stmt)

            return result.scalars().all()

    def update_analyzed_file_record(self, id, path: str | None = None, language: str | None = None):

        with self.Session() as session:
            record = session.get(AnalyzedFileRecord, id)

            if record is None:
                return None 

            if path is not None:
                record.path = path

            if language is not None:
                record.language = language

            session.commit()

            return record

    def delete_analyzed_file_record(self, id):

        with self.Session() as session:

            record = session.get(AnalyzedFileRecord, id)

            if record is None:
                return False

            session.delete(record)

            session.commit()

            return True
