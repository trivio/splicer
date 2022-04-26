from typing import Callable, Optional, Any

class Loc:
    current: Loc
    path: Optional[str]
    is_branch: Callable[[Any], bool]
    get_children: Callable[[Loc], Any]
    make_node: Callable[[Loc, Any], Any]
    
def zipper(root, is_branch, children, make_node) -> Loc: ...