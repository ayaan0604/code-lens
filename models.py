from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum

##Classes for File Info
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
    from_import : bool = False


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
    parent_class : Optional[str] = None
    return_annotation : Optional[str] = None
    parameters : List[ParameterInfo] = field(default_factory=list)
    
@dataclass
class CallInfo:
    qualified_name : str 
    line_number : int 
    containing_function : Optional[str] = None

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
    imports : List[ImportInfo] = field(default_factory=list)
    classes : List[ClassInfo] = field(default_factory=list)
    functions : List[FunctionInfo] = field(default_factory=list)
    calls : List[CallInfo] = field(default_factory=list)

#Class for dependency

class DependencyType(Enum):
    CALLS = "Calls"
    IMPORTS = "Imports"
    INHERITS = "Inherits"
    INSTANTIATES = "Instantiates"
@dataclass
class Dependency:
    source : Union[ClassInfo, FunctionInfo, Metadata]
    target : Union[ClassInfo, FunctionInfo, Metadata]
    type : DependencyType
    line : Optional[int] 

@dataclass
class ExternalDependency:
    module : str
    name : Optional[str] = None