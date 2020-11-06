FROM python:3.9-slim-buster

RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install and enable ssh service
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd
COPY ./sshd_config /etc/ssh/

COPY ./requirements.txt .

# install any build dependencies
RUN set -ex \
    && buildDeps="build-essential libpq-dev git default-libmysqlclient-dev libgeos-dev" \
    && deps="gdal-bin gettext" \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends \

# install python dependencies for project
RUN python -m pip install --upgrade pip setuptools wheel
    && python -m pip install -r requirements.txt \
    && python -m pip uninstall --yes django-easy-pdf \
    && python -m pip install git+https://github.com/pawanvirsingh/django-easy-pdf.git#egg=django-easy-pdf

# remove any unrequired dependencies
RUN apt-get purge -y --auto-remove $buildDeps \
       $(! command -v gpg > /dev/null || echo 'gnupg dirmngr') \

RUN mkdir media \
    && mkdir media/travel \
    && mkdir media/travel/temp \
    && mkdir media/inventory \
    && mkdir media/inventory/temp \
    && mkdir media/projects \
    && mkdir media/projects/temp \
    && mkdir media/ihub \
    && mkdir media/ihub/temp
#    && mkdir logs \
#    && touch error.log

COPY . /opt/services/djangoapp/src

EXPOSE 8000 2222

COPY ./azure_scripts/init.sh /usr/local/bin/
	
RUN chmod u+x /usr/local/bin/init.sh

ENTRYPOINT ["bash","init.sh"]
