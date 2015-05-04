from objectcube.vo import DimensionNode
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag

def test():
    tag = Tag(id=1, value='Test')
    dimension_service = get_service('DimensionService')
    db_node = dimension_service.add_dimension(tag)
    dimension_service.print_tree(db_node)

'''test()'''