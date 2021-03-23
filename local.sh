#!/bin/bash



# ----------------------------------------------------------------------------------------------#

# Update TL_BASE variable to match your project folder                                          #

# This script expects all  related repositories under same project folder.            #

# ----------------------------------------------------------------------------------------------#

TL_BASE="/ocr-receiving"

function tl_help {

    echo "====================================================================================="

    echo "USAGE   ./local.sh <Options> (i.e) ./local.sh up"

    echo "====================================================================================="

    echo "up            	# To start   environment" 
    echo "down-all      	# To stop entire dev including data/portainer environment"

    echo "network	    	# To create tvl-datanet network"

    echo "restart-ng    	# To restart NG containers only"

    echo "restart-search	# To restart Search (tl-web) containers only"

    echo "restart       	# To restart dev containers except data/portainer"

    echo "pull          	# Pull latest changes from GIT"

}

function tl_init {

	sudo mkdir -p $TL_BASE

	sudo chmod -R 777 $TL_BASE

	echo $TL_BASE

} 

function tl_status {

    y="sudo git ls-remote --heads https://github.com/Prabuatcontec/ocr-receiving.git"
    if diff <(git rev-parse HEAD | cut -b 1-30) <(eval "$y" | cut -b 1-30); then
    echo Not
    else
    file="static/uploads/0_update.txt"
    update=$(cat "$file")
    if update == 1
    git pull
    docker pull prabuatcontec/ocr-receiving
    docker-compose -f docker-compose.yml up --build
    fi
    fi
}

function tl_clone {
	cd $TL_BASE
}

function tl_build {
	docker pull prabuatcontec/ocr-receiving
}

function tl_up {
	sudo docker-compose -f docker-compose.yml up --build
}

function tl_read {
  file="static/uploads/0_update.txt" #the file where you keep your string name

  name=$(cat "$file")        #the output of 'cat $file' is assigned to the $name variable

  echo $name 
}

# set action

if [ -n "$1" ]; then

  TL_ACTION=$1

else

  TL_ACTION=help

fi


case $TL_ACTION in

  help)

    tl_help $@

    ;;

  init)

    tl_init $@

    ;;

  read)

    tl_read $@

    ;;


  status)

    tl_status $@


    ;;

  up)

    tl_up $@

    ;;

  pull)

    tl_gitpull $@

    ;;

  *)

    tl_error "Unknown action $TL_ACTION"

    tl_help

esac