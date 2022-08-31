import os
import sys
import requests
import time
import getopt
import logging
import hashlib
import shutil

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = None
Session = None

class Zims(Base):
	__tablename__ = 'zims'
	__table_args__ = {"extend_existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	size = Column(Integer)
	status = Column(String(32), index = True)
	timestamp = Column(Integer, index = True)

class Databases(Base):
	__tablename__ = 'databases'
	__table_args__ = {"extend_existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	reference = Column(String(256))
	timestamp = Column(Integer, index = True)	

class Files(Base):
	__tablename__ = 'files'
	__table_args__ = {"extend_existing": True}
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(256), index = True)
	ext = Column(String(32), index = True)
	md5 = Column(String(256))
	reference = Column(String(256))

HOST = "https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/"

HOST_SWARM = 'http://127.0.0.1:1635'
BATCH_ID_SWARM = ''

WAITING = "waitting"
DOWNLOADING = "downloading" 
EXTRACTING = "extracting"
UPLOADING = "uploading"
UPLOADED = "uploaded"

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)

#upload all files to swarm
def upload_file(name:str, dirs:str):
	totalcontent = 0
	filelist = []
	linklist = []

	rootpath = os.path.join(dirs, name)

	#collect file list for the dir
	for root, _, files in os.walk(rootpath):
		for file in files:
			filepath = os.path.join(root, file)
			if os.path.islink(filepath):
				linklist.append(filepath)
			else:
				filelist.append(filepath)

	#upload file list
	for filepath in filelist:

		relpath = '/' + os.path.relpath(os.path.dirname(filepath), rootpath)

		relname = os.path.join(relpath, os.path.basename(filepath))

		ext = 'resource'
		if relname.find('/A/') >= 0:
			ext = 'document'	

		md5sum = ''
		content = b''
		with open(filepath, 'rb') as f:
			content = f.read()

		if len(content) == 0:
			totalcnt += 1
			logging.info(f"ignore empty file: {filepath}")
			continue

		md5sum = hashlib.md5(content).hexdigest()

		while True:
			session = Session()
			try:
				fileInfo = session.query(FileStatus).filter(FileStatus.name == relname).first()
				if fileInfo is not None and fileInfo.md5 == md5sum:
					totalcnt += 1
					session.close()
					break

				reference = upload_file_to_swarm(content)
				#try again
				if reference is None:
					logging.warning(f"upload file: {filepath} to swarm failed")
					session.close()
					time.sleep(5)
					continue

				if fileInfo is None:
					session.add(FileStatus(name = relname, ext = ext, md5 = md5sum, reference = reference))
				else:
					fileInfo.md5 = md5sum
					fileInfo.reference = reference
				
				session.commit()
				totalcnt += 1
				logging.info(f"upload file: {filepath} success, reference: {reference}, total process: {totalcnt}/{len(filelist)}")
				session.close()
				break
			except:
				session.rollback()
			finally:
				session.close()

	for filepath in linklist:
		relpath = '/' + os.path.relpath(os.path.dirname(filepath), rootpath)

		relname = os.path.join(relpath, os.path.basename(filepath))

		linkname = '/' + os.readlink(filepath)

		session = Session()
		try:
			fileInfo = session.query(FileStatus).filter(FileStatus.name == linkname).first()
			if fileInfo is None:
				totalcnt +=1
				session.close()

			linkInfo = session.query(FileStatus).filter(FileStatus.name == relname).first()
			if linkInfo is None:
				session.add(FileStatus(name = relname, ext = fileInfo.ext, md5 = fileInfo.md5, reference = fileInfo.reference))
				session.commit()
				totalcnt += 1
				logging.info(f"upload link file: {filepath} success, reference: {fileInfo.reference}, total process: {totalcnt}/{len(filelist)}")
				session.close()			
			elif linkInfo.ext != fileInfo.ext or linkInfo.md5 != fileInfo.md5 or linkInfo.reference != fileInfo.reference:
				linkInfo.ext = fileInfo.ext
				linkInfo.md5 = fileInfo.md5
				linkInfo.reference = fileInfo.reference
				session.commit()
				totalcnt += 1
				session.close()
			else:
				totalcnt += 1
				session.close()
		except:
			session.close()


	#if all files upload success, update the status of the zim file status
	if totalcontent < len(filelist):
		return False

	return True

def upload_file_to_swarm(data):

	headers = {
		'Content-Type': 'application/octet-stream',
		'swarm-postage-batch-id': SWARM_BATCH_ID
	}

	res = requests.post(url = f"{SWARM_HOST}/bytes", headers = headers , data = data)

	if res.status_code >= 200 and res.status_code < 300:
		try:
			return res.json()['reference']
		except:
			return None

	return None


if __name__ == '__main__':
	argv = sys.argv[1:]

	extract = '/wiki/extract'
	dbname = '/wiki/wiki.db'

	#parse agrs
	try:
		opts, args = getopt.getopt(argv, "b:d:e:h:", [
			"batchid=",
			"host=",
            "extract=",
            "dbname"
        ])
	except:
		logging.error("parse arguments failed")
		sys.exit(-1)

	for opt, arg in opts:
		if opt in ['--extract', '-e']:
			extract = arg
		elif opt in ['--dbname', '-d']:
			dbname = arg	
		elif opt in ['--batchid', '-b']:
			SWARM_BATCH_ID = arg	
		elif opt in ['--host', '-h']:
			SWARM_HOST = arg									

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
			zimInfo = session.query(ZimStatus).filter(Zims.status == UPLOADING).order_by(Zims.timestamp).first();
			if zimInfo is None:
				session.close()
				logging.info("no zim files need to upload")
				time.sleep(120)
				continue
			else:
				res = upload_file(zimInfo.name, extract)
				if res:
					zimInfo.status = UPLOADED
					session.commit()
					logging.info(f"update zim file: {zimInfo.name} status to {UPLOADED} success")
					shutil.rmtree(os.path.join(extract, zimInfo.name))

					reference = upload_file_to_swarm(dbname)
					if reference is None:
						logging.error(f"update dbname: {dbname} to swarm failed")
					else:		
						session.add(DbStatus(name = dbname, reference = reference, timestamp = int(time.time())))
						session.commit()
						logging.info(f"update dbname: {dbname} to swarm success, new reference is: {reference}")			
				else:
					logging.error(f"update zim file: {zimInfo.name} status to {UPLOADED} failed")
		except:
			session.rollback()
		finally:
			session.close()

		time.sleep(120)			