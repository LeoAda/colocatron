init_dot_env:
	echo SECRET_KEY= > .env
	echo CURRENCY= >> .env
	echo MODE= >> .env

setup_win: init_dot_env
	python -m venv .venv
	.venv/Scripts/pip install -r requirements.txt

setup_linux: init_dot_env
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run_win:
	set PYTHONPATH=src;%PYTHONPATH% && waitress-serve --listen=0.0.0.0:8080 src.app:app