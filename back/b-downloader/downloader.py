import os
import sys
import time
import getopt
import logging
from urllib.request import urlretrieve
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = None
Session = None

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

#download zim file from the wikidumps website
def download_wiki_zim(name, dirs):

	filepath = os.path.join(dirs, name)

	if os.path.exists(filepath):
		os.remove(filepath)

	url = HOST + name

	def callback(blocknum, blocksize, totalsize):

		percent = 100.0 * blocknum * blocksize / totalsize

		if percent > 100:
			percent = 100

		percent = round(percent, 2)

		logging.info(f"downloading {name} to {dirs} in process {percent}%")


	try:
		urlretrieve(url, filepath, callback)
	except:
		return False

	if not os.path.exists(filepath):
		return False

	return True


if __name__ == '__main__':
	argv = sys.argv[1:]

	src = '/wiki/zim'
	dbname = '/wikipedia/wiki.db'

	#parse args
	try:
		opts, args = getopt.getopt(argv, "d:s:", [
            "dbname=",
            "src="
        ])
	except:
		logging.error("parse arguments failed")
		sys.exit(-1)

	for opt, arg in opts:
		if opt in ['--dbname', '-d']:
			dbname = arg
		elif opt in ['--src', '-s']:
			src = arg			

	#make download src dirs
	try:
		os.makedirs(src)
	except:
		if not os.path.exists(src):
			logging.error(f"make download dirs: {src} failed")
			sys.exit(-1)

	#create new sqlite engine
	engine = create_engine(f"sqlite:///{dbname}?check_same_thread=False", echo=False)

	#create Session maker
	Session = sessionmaker(bind = engine)			

	while True:

		session = Session()

		try:
			zimInfo = session.query(Zims).filter(Zims.status == DOWNLOADING).order_by(Zims.timestamp).first();
			if zimInfo is None:
				session.close()
				logging.info("no zim files need to download")
				time.sleep(120)
				continue
			else:
				res = download_wiki_zim(zimInfo.name, src)
				if res:
					zimInfo.status = EXTRACTING
					session.commit()
					logging.info(f"update zim file: {zimInfo.name} status to {EXTRACTING} success")
				else:
					logging.error(f"update zim file: {zimInfo.name} status to {EXTRACTING} failed")
		except:
			session.rollback()
		finally:
			session.close()

		time.sleep(120)