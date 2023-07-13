python -m pip install pip-tools
pip-compile --resolver=backtracking --generate-hashes --output-file=requirements.txt requirements.in
python -m pip install -r requirements.txt