#from python image
FROM python:3.9-slim-buster
WORKDIR /app

RUN apt-get update
RUN apt-get -y install build-essential

RUN python -m venv venv
RUN . venv/bin/activate
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python -m aquacrop.scripts.initiate_library

# copy the rest of the files
COPY . /app

# execute the streamlit command
CMD ["streamlit", "run", "Home.py"]
