CC=python3.9
install:
	apt-get update \
	$(CC) -m pip install -r requirements.txt
upgrade:
	$(CC) -m pip install -r requirements.txt --upgrade
clean:
	rm -rf *.png __pycache__/

.PHONY: clean