from models import *
from .models import *


def function_info_to_record(info: FunctionInfo, global_name: str):

    record = FunctionRecord(
        global_name=global_name,
        qualified_name=info.qualified_name,
        local_name=info.name,
        line_start=info.line_start,
        line_end=info.line_end,
        source=info.source,
        return_annotation=info.return_annotation,
        parent_class=info.parent_class
    )

    record.parameters = [
        ParameterRecord(
            name=pInfo.name,
            default=pInfo.default,
            annotation=pInfo.annotation
        )
        for pInfo in info.parameters
    ]

    return record


def function_record_to_info(record: FunctionRecord):

    info = FunctionInfo(
        name=record.local_name,
        qualified_name=record.qualified_name,
        line_start=record.line_start,
        line_end=record.line_end,
        source=record.source,
        parent_class=record.parent_class,
        return_annotation=record.return_annotation,
        parameters=[
            ParameterInfo(
                name=pinfo.name,
                default=pinfo.default,
                annotation=pinfo.annotation
            )
            for pinfo in record.parameters
        ]
    )

    return info


def metadata_to_file_record(metadata: Metadata):

    file_record = AnalyzedFileRecord(
        path=metadata.path,
        language=metadata.language,
        total_lines=metadata.total_lines,
        code_lines=metadata.code_lines
    )

    return file_record


def file_record_to_metadata(record: AnalyzedFileRecord):

    metadata = Metadata(
        path=record.path,
        language=record.language,
        total_lines=record.total_lines,
        code_lines=record.code_lines
    )

    return metadata


def parameter_info_to_record(info: ParameterInfo):

    record = ParameterRecord(
        name=info.name,
        default=info.default,
        annotation=info.annotation
    )

    return record


def parameter_record_to_info(record: ParameterRecord):

    info = ParameterInfo(
        name=record.name,
        default=record.default,
        annotation=record.annotation
    )

    return info


def import_info_to_record(info: ImportInfo):

    record = ImportRecord(
        module=info.module,
        imported_name=info.imported_name,
        alias=info.alias,
        line_number=info.line_number,
        from_import=info.from_import
    )

    return record


def import_record_to_info(record: ImportRecord):

    info = ImportInfo(
        module=record.module,
        imported_name=record.imported_name,
        alias=record.alias,
        line_number=record.line_number,
        from_import=record.from_import
    )

    return info


def  class_info_to_record(info: ClassInfo, global_name: str, functionRecords : dict):

    record = ClassRecord(
        name=info.name,
        qualified_name=info.qualified_name,
        global_name=global_name,
        line_no=info.line_number,
        bases=info.bases
    )

    record.methods = [
        functionRecords[method.qualified_name]
        for method in info.methods
    ]

    return record


def class_record_to_info(record: ClassRecord):

    info = ClassInfo(
        name=record.name,
        qualified_name=record.qualified_name,
        line_number=record.line_no,
        bases=record.bases,
        methods=[
            function_record_to_info(method)
            for method in record.methods
        ]
    )

    return info


def call_info_to_record(info: CallInfo):

    record = CallRecord(
        qualified_name=info.qualified_name,
        line_number=info.line_number,
        containing_function=info.containing_function
    )

    return record


def call_record_to_info(record: CallRecord):

    info = CallInfo(
        qualified_name=record.qualified_name,
        line_number=record.line_number,
        containing_function=record.containing_function
    )

    return info


def analyzed_file_to_record(
    analyzed_file: AnalyzedFile,
    global_names: dict
):

    record = metadata_to_file_record(analyzed_file.metadata)

    record.imports = [
        import_info_to_record(import_info)
        for import_info in analyzed_file.imports
    ]



    record.functions = [
        function_info_to_record(
            function,
            global_names[function.qualified_name]
        )
        for function in analyzed_file.functions
    ]

    function_records_map = {functionRecord.qualified_name : functionRecord 
                            for functionRecord in record.functions}

    record.classes = [
        class_info_to_record(
            cls,
            global_names[cls.qualified_name],
            function_records_map
        )
        for cls in analyzed_file.classes
    ]

    record.calls = [
        call_info_to_record(call)
        for call in analyzed_file.calls
    ]

    return record


def analyzed_file_record_to_analyzed_file(record: AnalyzedFileRecord):

    analyzed_file = AnalyzedFile(
        metadata=file_record_to_metadata(record),

        imports=[
            import_record_to_info(import_record)
            for import_record in record.imports
        ],

        classes=[
            class_record_to_info(class_record)
            for class_record in record.classes
        ],

        functions=[
            function_record_to_info(function_record)
            for function_record in record.functions
        ],

        calls=[
            call_record_to_info(call_record)
            for call_record in record.calls
        ]
    )

    return analyzed_file