if [[ "$VIRTUAL_ENV" != "" ]]
then
    echo " Virtual Environmnet [$VIRTUALENV] active. Uninstalling dependencies..."
    python -m pip uninstall -r requirements.txt -y
else
  echo "Please activate your virtual environment"
fi