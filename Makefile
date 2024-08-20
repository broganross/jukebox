

test:
	python -m pytest -s -v

test-cover:
	python -m pytest --cov=jukebox

mypy:
	mypy jukebox

build:
	python -m build

lint:
	python -m pylint jukebox
