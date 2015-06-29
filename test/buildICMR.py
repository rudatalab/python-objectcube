from objectcube.data_objects import *
from objectcube.factory import get_service
from base import ObjectCubeTestCase
from logging import getLogger

dim_file_name = '/Users/Bjorn/M3/Laugavegur/dimensions.txt'
tag_file_name = '/Users/Bjorn/M3/Laugavegur/laugavegur.txt'
img_path = u'/Users/Bjorn/M3/Laugavegur/photos/'


class ICMR(ObjectCubeTestCase):
    def __init__(self, *args, **kwargs):
        super(ICMR, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')
        self.concept_service = get_service('ConceptService')
        self.tag_service = get_service('TagService')
        self.dimension_service = get_service('DimensionService')
        self.tagging_service = get_service('TaggingService')
        self.logger = getLogger('ICMR')

    def _add_concept(self, title, description):
        concept = Concept(title=title, description=description)
        return self.concept_service.retrieve_or_create(concept)

    def _add_tag(self, value, description, concept):
        tag = Tag(value=value, description=description,
                  mutable=False, type=1L, concept_id=concept.id)
        return self.tag_service.add(tag)

    def _add_root(self, root_tag):
        return DimensionNode(root_tag_id=root_tag.id,
                             node_tag_id=root_tag.id,
                             child_nodes=[])

    def _add_node(self, parent_node, child_tag):
        node = DimensionNode(root_tag_id=parent_node.root_tag_id,
                             node_tag_id=child_tag.id,
                             child_nodes=[])
        parent_node.child_nodes.append(node)
        return node

    def _add_parent(self, parents, nodes, level, tag, node):
        parents[level] = tag
        nodes[level] = node
        level += 1
        return level, parents, nodes

    def _build_dimensions(self, file_name):
        level = 0
        parents = {}
        nodes = {}
        tags = {}

        current_concept = None
        concepts = {}

        dim_file = open(file_name, 'r')
        for line in dim_file:
            words = line.strip().split(':')
            if len(words) != 3:
                raise ObjectCubeException('Line too long or short')

            first = unicode(words[0])
            second = unicode(words[1])
            third = unicode(words[2])

            if first == u'Concept':
                if level > 0:
                    self.dimension_service.add(nodes[0])
                current_concept = self._add_concept(second, third)
                concepts[current_concept.id] = current_concept
                current_tag = self._add_tag(second, third, current_concept)
                tags[current_tag.value+':'+current_concept.title] =\
                    current_tag.id
                current_dim_node = self._add_root(current_tag)
                (level, parents, nodes) = \
                    self._add_parent(parents, nodes, 0,
                                     current_tag, current_dim_node)
            else:
                current_tag = self._add_tag(second, third, current_concept)
                tags[current_tag.value+':'+current_concept.title] =\
                    current_tag.id
                current_dim_node = self._add_node(nodes[level-1], current_tag)
                if second == parents[level-1].value:
                    (level, nodes, parents) = \
                        self._add_parent(parents, nodes, level,
                                         current_tag, current_dim_node)

        if level > 0:
            self.dimension_service.add(nodes[0])
        return tags

    def _add_object(self, name, path):
        object_ = Object(name=name, digest=path+name)
        return self.object_service.add(object_)

    def _build_taggings(self, file_name, path_to_images, tags):
        tag_file = open(file_name, 'r')
        for line in tag_file:
            self.logger.debug('BT: %s', repr(line))
            words = line.strip().split(':')
            image = unicode(words[0])
            current_object = self._add_object(image, path_to_images)
            for i in range(1, len(words)-2, 2):
                first = unicode(words[i])
                second = unicode(words[i+1])
                id_ = tags[second+':'+first]
                tagging = Tagging(tag_id=id_,
                                  object_id=current_object.id)
                self.tagging_service.add(tagging)

    def test_build_database(self):
        tags = self._build_dimensions(dim_file_name)
        self._build_taggings(tag_file_name, img_path, tags)
