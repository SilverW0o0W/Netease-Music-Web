# Pull base image.
FROM python:3.7.16

#工作目录
WORKDIR /data/Netease-Music-Web

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "src/music_web.py", "8090", "conf/music.toml" ]