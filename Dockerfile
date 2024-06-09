FROM python:3.9

WORKDIR /src

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install windows-curses

COPY . .

CMD ["python", "src/pythonmain.py"]