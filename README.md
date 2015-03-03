# python-objectcube
Implementation of the ObjectCube model, defined by Grimur Tomasson
&lt;grimurt@ru.is> and Bjorn Thor Jonsson &lt;bjorn@ru.is>.

# Install
This package has not been pushed to any global repository. However, it can be
installed the package from Github with pip as follows.

    pip install git+git://github.com/rudatalab/python-objectcube.git@master

If you need to install directly from another branch than master, you can change
the branch name after the at sign.

# Configure
This implementation of ObjectCube depends on PostgreSQL. To use it properly you
must point it a running PostgreSQL server with the required table schema.  This
schema can be found in the repository in a file named
[schema.sql](https://raw.githubusercontent.com/rudatalab/python-objectcube/master/schema.sql).

Database connection settings are configured with environment variables. The
most important variables to configure are the following.

    export OBJECTCUBE_DB_HOST=..
    export OBJECTCUBE_DB_USER=..
    export OBJECTCUBE_DB_PORT=..
    export OBJECTCUBE_DB_NAME=..
    export OBJECTCUBE_DB_PASSWORD=..

# Running tests
To run the test, you must have PostgreSQL installed. If not you must install
it. For Linux distributions with the Apt package manger, type in the following.

The scripts helps with initialising your own cluster

    sudo apt-get install postgresql postgresql-contrib postgresql-server-dev-{version or all}

If this is your local workstation, you should disable PostgreSQL for starting
up on boot time.

    sudo update-rc.d -f postgresql remove
    sudo service postgresql stop

On OS X, we suggest that you use [Homebrew](http://brew.sh/). You can find good
setup instructions on their web page.

    brew install postgresql

You can than use the help scripts in the repository to initialize as a test
PostgreSQL cluster for running the test.
    
    scripts/objectcube setup

After that you can run

    scripts/objectcube run_tests

Note that this command will start a PostgreSQL server in background. To start the server you can
use the scripts as follows.

    scripts/objectcube stop_postgres

The server can also be started with

    scripts/objectcube start_postgres

## API

Actions are performed through stateless services. The services that are now offerred are 

- TagService
- ObjectService
- DimensionService

Service are obtained using a service factory as follows.

	from objectcube.factory import get_service
	tag_service = get_service('TagService')

The class implementing the service is configured in `objectcube.settings.FACTORY_CONFIG`. Each service must implement a relevant base class in `objectcube.services.base`.

### TagService
The TagService manages tags.

#### get_by_value(value)
Fetches tags by value (name). This function returns a list of `objectcube.vo.Tag` objects.

#### get_by_id(id)
#### count()
#### get_tags(offset=0, limit=100)
#### add_tag(tag)

### ObjectService
Manages objects
#### count()
#### add_tags_to_objects(objects, tags):
#### get_objects_by_tags(tags)
#### get_objects(offset=0, limit=10)

