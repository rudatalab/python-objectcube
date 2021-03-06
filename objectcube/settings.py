import os

# Database configurations.
DB_HOST = os.environ.get('OBJECTCUBE_DB_HOST', 'localhost')
DB_USER = os.environ.get('OBJECTCUBE_DB_USER', os.environ.get('LOGNAME'))
DB_PORT = int(os.environ.get('OBJECTCUBE_DB_PORT', 5432))
DB_DBNAME = os.environ.get('OBJECTCUBE_DB_NAME', os.environ.get('LOGNAME'))
DB_PASSWORD = os.environ.get('OBJECTCUBE_DB_PASSWORD',
                             os.environ.get('LOGNAME'))
DB_MEASURE = int(os.environ.get('OBJECTCUBE_MEASURE', False))

# Concept service configuration.
FACTORY_CONFIG = {
    'TagService': 'objectcube.services.impl.postgresql.tag.'
                  'TagService',

    'DimensionService': 'objectcube.services.impl.postgresql.dimension.'
                  'DimensionService',

    'ObjectService': 'objectcube.services.impl.postgresql.object.'
                     'ObjectService',

    'BlobService': 'objectcube.services.impl.filesystem.'
                   'blob_service.FileBlobService',

    'ConceptService': 'objectcube.services.impl.postgresql.concept.'
                  'ConceptService',

    'PluginService': 'objectcube.services.impl.postgresql.plugin.'
                  'PluginService',

    'TaggingService': 'objectcube.services.impl.postgresql.tagging.'
                  'TaggingService',
}

PLUGINS = (
    'objectcube.plugin.exif.ExifPlugin'
)
