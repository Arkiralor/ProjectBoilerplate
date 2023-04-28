if [[ "$VIRTUAL_ENV" != "" ]]
then
    echo " Virtual Environmnet [$VIRTUALENV] active. Installing dependencies..."
    python -m pip install --no-cache pip-tools
    pip-compile
    python -m pip install --no-cache -r requirements.txt
else
  echo "Please activate your virtual environment"
fi