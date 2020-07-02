FROM python:3.8

RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN python -m pip install --upgrade pip setuptools wheel
#RUN apk add libmysqlclient-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN python create_env_file.py --devops-build-number $(Build.BuildNumber)
RUN mkdir media
RUN mkdir media/travel
RUN mkdir media/travel/temp
RUN mkdir media/inventory
RUN mkdir media/inventory/temp

COPY . /opt/services/djangoapp/src

EXPOSE 8000

COPY init.sh /usr/local/bin/
	
RUN chmod u+x /usr/local/bin/init.sh
ENTRYPOINT ["init.sh"]
