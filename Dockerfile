# Use an official Python runtime as a parent image
FROM python:3.8

# Copy the current directory contents into the container at /app
COPY . /app
ENV PATH=$PATH:.
ENV PYTHONPATH=/app

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt

CMD python /app/jeebee/bot.py
