isFunction() { [[ "$(declare -Ff "$1")" ]]; }

function cout {
    COLOR=2
    if [ -n "$2" ]; then
        COLOR=$2
    fi

	echo "$(tput setaf $COLOR)$1$(tput sgr0)";
};