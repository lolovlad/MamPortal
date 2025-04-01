FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN chmod a+x docker/*.sh
