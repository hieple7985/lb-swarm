import os  
from urllib.request import urlretrieve
  
HOST = "https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/"   

def download_wikipedia_zim(name, dirs):

	filepath = os.path.join(dirs, name)

	if os.path.exists(filepath):
		os.remove(filepath)

	url = HOST + name

	def callbackfunc(blocknum, blocksize, totalsize):

		percent = 100.0 * blocknum * blocksize / totalsize

		if percent > 100:
			percent = 100

		percent = round(percent, 2)

		print(f"downloading {name} to {dirs} in process {percent}%")


	try:
		urlretrieve(url, filepath, callbackfunc)
	except:
		return False

	if not os.path.exists(filepath):
		return False

	return True


file_name = "wiktionary_vi_all_nopic_2022-07.zim"

file_path = "~/laSwarm/zim"

download_wikipedia_zim(file_name,file_path)