#https://github.com/svx/poetry-fastapi-docker/blob/main/pyproject.toml
# Dockerfile
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

# Creating a python base with shared environment variables
FROM python:3.11.4-bullseye
SHELL ["/bin/bash", "-c"]

RUN apt update
RUN apt install wget make  libftdi-dev libusb-dev -y
RUN git clone https://github.com/13-37-org/infnoise
WORKDIR infnoise/software
RUN git checkout tags/0.3.3
RUN make -f Makefile.linux
RUN make -f Makefile.linux install
WORKDIR /
RUN mkdir /trng-api
WORKDIR /trng-api
COPY /trng-api /trng-api

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root

CMD [ "uvicorn", "main:app", "--reload"]