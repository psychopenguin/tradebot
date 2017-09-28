FROM python:3.6-alpine
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt
COPY tradebot/ /tradebot
COPY run_bot.py /

