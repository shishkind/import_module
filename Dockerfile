FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /test_app/
COPY . .
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN apt-get -y install unixodbc-dev
RUN pip install pyodbc
RUN pip install tk
RUN pip install -r requirements.txt
