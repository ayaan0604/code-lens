from dataclasses import dataclass, field
from typing import List, Optional



@dataclass
class Metadata:
    path : str
    language : str
    total_lines : int
    code_lines : int


@dataclass
class ImportInfo:  
    module : str 
    imported_name : str 
    alias : str
    line_number : int


@dataclass
class ParameterInfo:
    name : str
    default : Optional[str] = None
    annotation : Optional[str] = None

@dataclass
class FunctionInfo:
    name : str 
    qualified_name : str
    line_start : int 
    line_end : int 
    source : str
    parent_class : Optional[str] 
    return_annotation : Optional[str]
    parameters : List[ParameterInfo] = field(default_factory=list)
    
@dataclass
class CallInfo:
    qualified_name : str 
    line_number : int 
    containing_function : Optional[str]

@dataclass
class ClassInfo:
    name : str
    qualified_name : str 
    line_number : int
    bases : List[str]  = field(default_factory=list)
    methods : List[FunctionInfo]  = field(default_factory=list)
    


@dataclass
class AnalyzedFile:
    metadata : Metadata
    imports : List[ImportInfo]
    classes : List[ClassInfo]
    functions : List[FunctionInfo]
    calls : List[CallInfo]