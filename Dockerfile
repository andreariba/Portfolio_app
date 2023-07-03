FROM python:3.11.3-slim

#ENV MONGO_DB_USERNAME=admin \
#    MONGO_DB_PWD=password

RUN apt-get update && \
    apt-get install -y git

WORKDIR /home

RUN git clone https://github.com/andreariba/Portfolio_app.git

WORKDIR /home/Portfolio_app

#RUN pip install --upgrade pip
RUN pip install --upgrade pip && \
    pip install \
        pandas \
        dash \
        dash-bootstrap-components \
        pymongo \
        copulas \
        yfinance \
        newsapi-python \
        transformers

CMD ["python", "index.py"]

EXPOSE 8050