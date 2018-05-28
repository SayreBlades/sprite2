#####################################################
# build
#####################################################
FROM lambci/lambda:build-python3.6 as build

COPY sprite2 sprite2
COPY setup.py .
RUN pip install -e .

RUN pip install flake8
RUN flake8

RUN pip install mypy
RUN mypy sprite2 --ignore-missing-imports

ARG REQUIREMENTS="cloudpickle dask"
RUN pip install -t . $REQUIREMENTS
RUN zip -FSqr lambda.zip .


#####################################################
# invoke
#####################################################
FROM lambci/lambda:python3.6 as invoke
COPY --from=build /var/task .


#####################################################
# deploy
#####################################################
FROM python:3.6-slim
RUN pip install awscli
WORKDIR /tmp/lambda/
COPY --from=build /var/task /tmp/lambda/
ENTRYPOINT ["aws", "lambda", "update-function-code", "--zip-file", "fileb://lambda.zip", "--function-name"]
CMD sprite
