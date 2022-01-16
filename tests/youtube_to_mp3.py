from __future__ import unicode_literals
import youtube_dl
import os
import re

# Remove all existing mp3s in the file
for f in filter(lambda x: ".mp3" in x, os.listdir()):
    os.remove(f)
#
# print("Insert the link")
# link = input ("")
name = input("Song Name: ")
# Make sure name is valid
regex = re.compile('[@_!#$%^&*()<>?/\|}{~: .]')
if regex.search(name) is not None:
    print("Invald name")

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    print("Return", ydl.download([link]))

# Move mp3 to proper location with correct name
f = list(filter(lambda x: ".mp3" in x, os.listdir()))[0]
dest = os.path.join(os.environ["MUSIC_PATH"], name + ".mp3")
os.rename(f, dest)
print(f"File moved to {dest}")
