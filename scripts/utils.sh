isFunction() { [[ "$(declare -Ff "$1")" ]]; }

function cout {
    COLOR=2
    if [ -n "$2" ]; then
        COLOR=$2
    fi

	echo "$(tput setaf $COLOR)$1$(tput sgr0)";
};

function cmd_startpostgres {
  pg_ctl -D $POSTGRES_DATA_DIR -l $ROOT_DIR/postgres.log -w start
  cout "Postgres started"
}

function cmd_stoppostgres {
  cout "Stopping postgres in $POSTGRES_DATA_DIR"
  pg_ctl -D $POSTGRES_DATA_DIR stop -s -m fast -w
}
