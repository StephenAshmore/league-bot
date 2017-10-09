FROM python:3.6

# Copying the requirements for installation to take
# advantage of the caching.
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY * /

CMD python main.py