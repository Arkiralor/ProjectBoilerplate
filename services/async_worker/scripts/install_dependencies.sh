python -m pip install pip-tools
pip-compile
python -m pip install -r requirements.txt
python -m spacy download en_core_web_md