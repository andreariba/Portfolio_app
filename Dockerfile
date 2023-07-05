FROM python:3.11.3-slim

RUN apt-get update && \
    apt-get install -y git

RUN pip install --upgrade pip && \
    pip install \
        pandas \
        dash \
        dash-bootstrap-components \
        pymongo \
        copulas \
        yfinance

WORKDIR /home


ARG APP_VER=unknown

RUN git clone https://github.com/andreariba/Portfolio_app.git

WORKDIR /home/Portfolio_app

CMD ["python", "index.py"]

EXPOSE 8050