FROM python
RUN mkdir /temp
WORKDIR /temp
RUN git clone https://github.com/dn1z/pgn2gif .
RUN pip install -r requirements.txt
RUN python setup.py install
RUN mkdir /app
RUN mkdir /app/output
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python telebot.py