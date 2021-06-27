CC=python3.9

all:
	chmod +x ./launcher.sh && \
	./launcher.sh
install:
	apt-get update && \
	$(CC) -m pip install poetry --upgrade && \
	poetry config virtualenvs.create false && \
	poetry install --no-dev
upgrade:
	$(CC) -m pip install pip --upgrade && \
	$(CC) -m pip install -r requirements.txt --upgrade
clean:
	rm -rf *.png __pycache__/

.PHONY: clean