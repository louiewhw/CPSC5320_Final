# this is an official Python runtime, used as the parent image
FROM python:3.7.2

# set the working directory in the container to /app
WORKDIR /app

# add the current directory to the container as /app
ADD . /app

# execute everyone's favorite pip command, pip install -r
RUN pip install --trusted-host pypi.python.org -r requirements.txt && \
    apt-get install -y git



# execute the Flask app
EXPOSE 8000
CMD python app.py
