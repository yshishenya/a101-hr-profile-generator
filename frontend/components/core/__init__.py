"""
Core Components module.

!>45@68B >A=>2=K5 187=5A-:><?>=5=BK A8AB5<K:
- SearchComponent: >8A: 4>;6=>AB59 A@548 4,376 ?>78F89
- GeneratorComponent: 5=5@0F8O ?@>D8;59 4>;6=>AB59 G5@57 LLM
- ProfileViewerComponent: @>A<>B@ 8 >B>1@065=85 A35=5@8@>20==KE ?@>D8;59
- FilesManagerComponent: !:0G820=85 D09;>2 2 JSON/Markdown D>@<0B0E
"""

from .search_component import SearchComponent
from .generator_component import GeneratorComponent
from .profile_viewer_component import ProfileViewerComponent
from .files_manager_component import FilesManagerComponent

__all__ = [
    "SearchComponent",
    "GeneratorComponent", 
    "ProfileViewerComponent",
    "FilesManagerComponent"
]