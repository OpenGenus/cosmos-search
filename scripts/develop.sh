################################################################################
# helper functions
################################################################################
assert()
{
    actual_error_code=$?

    expect_error_code=0
    if [ $# != 0 ]; then
        expect_error_code=$1
    fi

    if [ $actual_error_code -ne $expect_error_code ]; then
        echo "exit ($actual_error_code)"
        exit 1
    fi
}


################################################################################
# test version of python and pip
################################################################################
PIP=`which pip3`
assert
PYTHON=`which python3`
assert

################################################################################
# test venv
################################################################################
if [ "$VIRTUAL_ENV" == '' ]; then
    echo "Please run as venv:"
    echo "    PYTHON -m venv env"

    # help to create venv
    echo "Type the venv-name if you want to create venv, or type Ctrl+C to exit."
    name=''
    while [ "$name" == '' ]
    do
        read name
    done

    # test venv folder is existed or not
    tmp=`ls $name 2>/dev/null`
    if [ $? == 0 ]; then
        echo "Are you want to override the '$name'? (y/n [n])"
        read answer

        if [ "$answer" != 'y' ] && [ "$answer" != 'yes' ]; then
            echo "not overwritten"
            exit 0
        else
            rm -rf $name
        fi
    fi


    echo "Creating venv ..."
    $PYTHON -m venv $name
    echo "Please type following command and run this script again:"
    echo "    source $name/bin/activate"
    exit 1
fi

################################################################################
# main
################################################################################

tmp=`ls \.env 2>/dev/null`
if [ $? == 1 ]; then
    cp .env.example .env
fi
$PIP install -r requirements.txt
$PYTHON manage.py createcachetable
$PYTHON manage.py collectstatic
$PYTHON manage.py migrate

echo
echo "Run server by following command:"
echo "    $PYTHON manage.py runserver"
