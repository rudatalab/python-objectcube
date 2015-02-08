# python-objectcube
Implementation of the ObjectCube model, defined by Grimur Tomasson
&lt;grimurt@ru.is> and Bjorn Thor Jonsson &lt;bjorn@ru.is>

# Install
We currently don't have a ready release for this module and we have not pushed
it to any global repository.

To use this library in other Python projects, you can install the package
directly into your project, using Pip, from Github as follows.

    pip install git+git://github.com/rudatalab/python-objectcube.git@master
    
The last parameter is the name of the branch that you want to clone from. We
look at master as the next release candidate, so this branch should always be
safe to install.

##Running tests
Currently, for running the test, you must have a running PostgreSQL instance on
your machine. No worries, the scripts helps with initialising your own cluster
and running. But you must have PostgreSQL installed.

On most nix-like operating system such as Ubuntu on OS X this step is
relatively easy

For Ubuntu users

    sudo apt-get install postgresql postgresql-contrib
    
If this is your local workstation, you should disable PostgreSQL for starting
up on boot time.

    sudo update-rc.d -f postgresql remove
    sudo service postgresql stop

On OS X, we suggest that you use [Homebrew](http://brew.sh/). You can find good
setup instructions on their web page, so they will not be uttered here (which
movie reference was that?)

    brew install postgresql
    
With that said, let us run the tests

    scripts/objectcube create_virtualenv
    scripts/objectcube init_postgresql_cluster
    scripts/objectcube start_postgres

After this, your terminal will be occupied with running, and showing you
PostgreSQL output.

Now, open up a new terminal, and we initialize our PostgreSQL cluster with our
database schema.

    scripts/objectcube create_database_schema
    
After this, you can run the tests, as often as you like throughout your
development with

    scripts/objectcube run_test

Note that you must have the PostgreSQL terminal up and running while you are
running the tests.
    
