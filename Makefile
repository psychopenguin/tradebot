build:
	docker build . -t psychopenguin/tradebot

push:
	docker push psychopenguin/tradebot

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

all: build push
