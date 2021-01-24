FROM orgoro/dlib-opencv-python:3.8

WORKDIR /usr/src

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
   && unzip awscliv2.zip \
   && ./aws/install

COPY ./requirements.txt .

RUN pip install -r requirements.txt

ENV PYTHONPATH=/usr/src

COPY ./app ./app

CMD sleep 20 && python ./app/run.py