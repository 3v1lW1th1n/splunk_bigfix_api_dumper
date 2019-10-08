#!/usr/bin/bash

# read in authentication token from splunk
read tok 

# debug arguments
echo $(env)
echo TOKEN: $tok 


# script mode variables
APP_LOCATION="$SPLUNK_HOME/etc/apps/bigfix_api_dumper"
SCRIPT_CONFIG="$APP_LOCATION/local/bigfix_api_dumper.conf"
SCRIPT_ARGS="relevance -c $SCRIPT_CONFIG"
SCRIPT_LOCATION="$APP_LOCATION/bin/bigfix_api_dumper.py"
SCRIPT_CMD="$SCRIPT_LOCATION $SCRIPT_ARGS"
VENV_PATH="$APP_LOCATION/bin/venv"
# debug SCRIPT_CMD
echo $SCRIPT_CMD

# create the venv
if [[ ! -d $VENV_PATH ]];
then
    echo "attempting to configure virtualenv"
    /usr/bin/virtualenv-3 $VENV_PATH
    source $VENV_PATH/bin/activate
    # install prereqs
    pip3 install requests lxml
    deactivate
fi

# call python 3 to execute the bigfix api dumper script
source $VENV_PATH/bin/activate
/usr/bin/python3 $SCRIPT_CMD
