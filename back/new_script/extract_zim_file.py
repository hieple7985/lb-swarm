import os  
import re
import shutil
import subprocess
  
HOST = "https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/"   

#extract zim file to dst dirs using zimdump
def extract_wikipedia_zim(name, src, dst):

	srcpath = os.path.join(src, name)

	if not os.path.exists(srcpath):
		return False

	if re.match('^[a-zA-Z0-9]', name) is None:
		return False

	dstpath = os.path.join(dst, name)
	if os.path.exists(dstpath):
		shutil.rmtree(dstpath)

	cmd = '\home\laSwarm\kiwix-tools_linux-x86_64-3.1.1\zimdump dump --dir={0} {1}'.format(dstpath, srcpath)
	res = subprocess.Popen(cmd, shell = True, stdout = None, stderr = None).wait()

	if res != 0:
		return False

	return True

src = "~\laSwarm\zim"
extract = "~\laSwarm\content"
file_name = "wikipedia_vi_all_mini_2022-08.zim"
extract_wikipedia_zim(file_name,src,extract)

