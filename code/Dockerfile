#from python image
FROM python:3.10-slim-buster
WORKDIR /app

RUN python -m venv venv
RUN . venv/bin/activate
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy the rest of the files
COPY . /app

# execute the streamlit command
CMD ["streamlit", "run", "Home.py"]