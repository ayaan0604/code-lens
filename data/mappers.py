from models import *
from .models import *

def function_info_to_record(info : FunctionInfo, global_name: str):

    record = FunctionRecord(
        global_name = global_name,
        qualified_name = info.qualified_name,
        local_name = info.name,
        line_start = info.line_start,
        line_end = info.line_end,
        source = info.source,
        return_annotation = info.return_annotation,
        parent_class = info.parent_class
    )

    record.parameters = [
        ParameterRecord(
            name = pInfo.name,
            default = pInfo.default,
            annotation = pInfo.annotation
        ) for pInfo in info.parameters
    ]

    return record

def function_record_to_info(record: FunctionRecord):
    info = FunctionInfo(
        name = record.local_name,
        qualified_name= record.qualified_name,
        line_start= record.line_start,
        line_end= record.line_end,
        source = record.source,
        parent_class= record.parent_class,
        return_annotation= record.return_annotation,
        parameters= [
            ParameterInfo(
                name = pinfo.name,
                default= pinfo.default,
                annotation= pinfo.annotation
            ) for pinfo in record.parameters
        ]

    )

    return info

