import os

# Database configurations.
DB_HOST = os.environ.get('OBJECTCUBE_DB_HOST', 'localhost')
DB_USER = os.environ.get('OBJECTCUBE_DB_USER', os.getlogin())
DB_PORT = int(os.environ.get('OBJECTCUBE_DB_PORT', 5432))
DB_DBNAME = os.environ.get('OBJECTCUBE_DB_NAME', os.getlogin())
DB_PASSWORD = os.environ.get('OBJECTCUBE_DB_PASSWORD', os.getlogin())

# Concept service configuration.
FACTORY_CONFIG = {
    'TagService': 'objectcube.services.impl.postgresql.tag.'
                  'TagServicePostgreSQL',
    'DimensionService': 'objectcube.services.impl.postgresql.dimension.'
                  'DimensionServicePostgreSQL',
}

PLUGINS = (
    'objectcube.plugin.exif.ExifPlugin'
)
