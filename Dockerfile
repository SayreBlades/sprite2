#####################################################
# build
#####################################################
FROM lambci/lambda:build-python3.6 as build

COPY app.py .
COPY requirements.txt .

RUN pip install flake8
RUN flake8

RUN pip install mypy
RUN mypy app.py --ignore-missing-imports

RUN pip install -r requirements.txt -t .
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