FROM python:3.11.3

WORKDIR /usr/src/

COPY requirements.txt requirements.dev.txt /usr/src/

RUN pip install --no-cache-dir -r requirements.txt -r requirements.dev.txt

RUN pip --no-cache-dir install --upgrade awscli

ENV FBN_LUSID_API_URL ${FBN_LUSID_API_URL}
ENV FBN_LUSID_ACCESS_TOKEN ${FBN_LUSID_ACCESS_TOKEN}

ENTRYPOINT PYTHONPATH=/usr/src/:/usr/src/tutorials python -m unittest discover -v
