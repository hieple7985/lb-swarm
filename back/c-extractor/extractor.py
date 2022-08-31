import os
import sys
import time
import re
import getopt
import logging
import shutil
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

class Zims(Base):
	__tablename__ = 'zims'
	__table_args__ = {"existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	size = Column(Integer)
	status = Column(String(32), index = True)
	timestamp = Column(Integer, index = True)

class Databases(Base):
	__tablename__ = 'databases'
	__table_args__ = {"existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	reference = Column(String(256))
	timestamp = Column(Integer, index = True)	

class Files(Base):
	__tablename__ = 'files'
	__table_args__ = {"existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	ext = Column(String(32), index = True)
	md5 = Column(String(256))
	reference = Column(String(256))

HOST = "https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/"

WAITING = "waitting"
DOWNLOADING = "downloading" 
EXTRACTING = "extracting"
UPLOADING = "uploading"
UPLOADED = "uploaded"

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)


#extract zim file to dst dirs using zimdump
def extract_wiki_zim(name, src, dst):

	srcpath = os.path.join(src, name)

	if not os.path.exists(srcpath):
		return False

	if re.match('^[a-zA-Z0-9]', name) is None:
		return False

	dstpath = os.path.join(dst, name)
	if os.path.exists(dstpath):
		shutil.rmtree(dstpath)

	cmd = '~/zim-tools_linux-x86_64-3.1.1/zimdump dump --dir={0} {1}'.format(dstpath, srcpath)
	res = subprocess.Popen(cmd, shell = True, stdout = None, stderr = None).wait()

	if res != 0:
		return False

	return True

if __name__ == '__main__':
	argv = sys.argv[1:]

	src = '/wiki/zim'
	extract = '/wiki/doc'
	dbname = '/wiki/wiki.db'

	#parse agrs
	try:
		opts, args = getopt.getopt(argv, "d:e:s:", [
            "src=",
            "extract=",
            "dbname"
        ])
	except:
		logging.error("parse arguments failed")
		sys.exit(-1)

	for opt, arg in opts:
		if opt in ['--src', '-s']:
			src = arg
		elif opt in ['--extract', '-e']:
			extract = arg
		elif opt in ['--dbname', '-d']:
			dbname = arg			

	#make dst dirs
	try:
		os.makedirs(extract)
	except:
		if not os.path.exists(extract):
			logging.error(f"make extract dirs: {extract} failed")
			sys.exit(-1)

	#create new sqlite engine
	engine = create_engine(f"sqlite:///{dbname}?check_same_thread=False", echo=False)

	#create Session maker
	Session = sessionmaker(bind = engine)

	while True:

		session = Session()

		try:
			zimInfo = session.query(Zims).filter(Zims.status == EXTRACTING).order_by(Zims.timestamp).first()
			if zimInfo is None:
				session.close()
				logging.info("no zim files need to extract")
				time.sleep(120)
				continue
			else:
				res = extract_wiki_zim(zimInfo.name, src, extract)
				if res:
					zimInfo.status = UPLOADING
					session.commit()
					os.remove(os.path.join(src, zimInfo.name))
					logging.info(f"update zim file: {zimInfo.name} status to {UPLOADING} success")
				else:
					logging.error(f"update zim file: {zimInfo.name} status to {UPLOADING} failed")
		except:
			session.rollback()
		finally:
			session.close()

		time.sleep(120)