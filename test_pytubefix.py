from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://www.youtube.com/shorts/Pn5-EZxajro"

yt = YouTube(url, use_po_token=True)
print(yt.title)
ys = yt.streams.get_lowest_resolution()
ys.download()
print("Downloaded")
