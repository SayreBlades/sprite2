# Sprite2

Sprite2 is a distributed python execution environment intended for analytics-based work loads.  It supports adhoc function execution based on serverless technologies and dask.

The purpose of Sprite2 is to provide a way to help scale your batchy workloads with as little operational overhead as possible.  Many solutions (like Spark, dask distributed, etc...) require a dedicated cluster of machines.  The operational effort to setup and support a dedicated cluster is not trivial.  Sprite2 does not have this requirement. It uses AWS lambda to scale its computational needs.


## Example Usage

[basic](https://github.com/SayreBlades/sprite2/blob/master/examples/1_basic.ipynb)

[dask](https://github.com/SayreBlades/sprite2/blob/master/examples/2_dask.ipynb)


## Installation

### AWS Environment

Currently, usage of this library depends heavily on AWS. Lambda is the serverless execution backend.  As such, running all `spark2` scripts (see below) will assume that your AWS credentials are environmentally available in the AWS standard way.  See: [configuring the AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

```
aws configure --profile [name]
```

### Python

Use of [virtualenv](http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python) is recommended.

Run this command to install dependencies::

```
pip install -r requirements.txt
```

Then install ``sprite2`` itself:

```
pip install -e .
```

To verify your installation, run tests:

```
pytest
```


## Whats in here?

### The Remote Executor

This function takes your ad-hoc client function, executes it, and returns the result.

It's important to note that the executor has the same dependencies as your client code.  For example, if you are operating on numpy arrays, your executor should have the same numpy dependency as your client code.  This is maintained via the requirements.txt file.

###  The Deployment Scripts

It uses AWS cloudformation to define the function details and IAM role's necessary for its execution.  The cloudformation template is found under `config/cloudformation.yaml`.

To create the sprite function on aws lambda:

```
AWS_PROFILE=[name] sprite2 create
```

To delete the sprite function on aws lambda:

```
AWS_PROFILE=[name] sprite2 delete
```

To update the sprite function on aws lambda.  The only reason to do this would be to update dependencies:

```
AWS_PROFILE=[name] sprite2 update 
```

### Python Client Library

Wraps up the AWS lambda calls, serialization, deserialization, as well as a dask backend implementation.


### Example Python Notebooks

To run the jupyter notebook, dont forget to expose the nb server to your AWS environment:

```
> AWS_PROFILE=[name] jupyter notebook
```


## TODO:

- more tests
- handle remote errors better (i.e. re-raise original)
- better scripts
- better logging for diagnostics