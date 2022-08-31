import getopt
import logging
import re
import sys
import time
from threading import Thread
import requests
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
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

WAITING = "waitting"
DOWNLOADING = "downloading" 
EXTRACTING = "extracting"
UPLOADING = "uploading"
UPLOADED = "uploaded"

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)

#parse timestamp
def parse_timestamp(timestamp, timeformat = '%d-%b-%Y %H:%M'):

	t = time.strptime(timestamp, timeformat)

	return int(time.mktime(t))

#parse file size
def parse_size(size = 0.0):

	if size < 1024:
		return '{0} B'.format(round(size, 2))
	else:
		size /= 1024.0

	if size < 1024.0:
		return '{0} KB'.format(round(size, 2))
	else:
		size /= 1024.0

	if size < 1024:
		return '{0} MB'.format(round(size, 2))
	else:
		size /= 1024.0

	if size < 1024:
		return '{0} GB'.format(round(size, 2))
	else:
		size /= 1024.0

	if size < 1024:
		return '{0} TB'.format(round(size, 2))
	else:
		size /= 1024.0		

	return '{0} PB'.format(round(size, 2))

#get wiki zim list
def get_wiki_dumps(host = HOST):

	res = requests.get(host)

	if res.status_code >= 200 and res.status_code < 300:
		regexp = r'\>(wikipedia\S{1,}\.zim)\<\S{1,}\s{1,}(\S{1,}\s{1,}\S{1,})\s{1,}(\d{1,})'
		return re.findall(regexp, res.text)
	else:
		logging.error(f"get wikipedia dumps error: {res.text}")

	return None

#parse wiki dumps
def parse_wiki_dumps(data = []):

	res = []

	if data is None:

		return res

	for d in data:

		name, timestamp, size = d

		res.append([name, int(size), parse_timestamp(timestamp)])
	
	return sorted(res, key = lambda x: x[2])

#update zim dump list
def update_zim_dump_list():
	while True:

		try:
			dumps = parse_wiki_dumps(get_wiki_dumps())

			for dump in dumps:
				session = Session()
				name, size, timestamp = dump

				try:
					zimInfo = session.query(Zims).filter(Zims.name == name).first()
					if zimInfo is None:
						session.add(Zims(name = name, size = size, timestamp = timestamp, status = WAITING))
						session.commit()
						logging.info(f"add new zim file: {name}, size: {parse_size(size)}, time:{timestamp}, status: {WAITING}")
					elif zimInfo.timestamp > timestamp or zimInfo.size != size:
						logging.info(f"zim update {zimInfo.timestamp}, {timestamp}, {zimInfo.size}, {size}")
						session.query(Zims).filter(Zims.name == name).update({Zims.size: size, Zims.timestamp: timestamp, Zims.status: WAITING})
						session.commit()
						logging.info(f"update new zim file: {name}, size: {parse_size(size)}, time:{timestamp}, status: {WAITING}")
				except:
					logging.error(f"update zim file: {name}, size: {parse_size(size)}, time:{timestamp}, status: {WAITING} failed")
				finally:
					session.close()
		except:
			time.sleep(3600)

		#update every day
		time.sleep(86400)

#trigger a zim file to downloading status
def trigger_wiki_downloading():
	session = Session()

	try:
		zimInfos = session.query(Zims).order_by(Zims.timestamp).all();
		if zimInfos is None:
			session.close()
			return

		for ziminfo in zimInfos:
			if ziminfo.status == UPLOADED:
				continue
			elif ziminfo.status == WAITING:
				session.query(Zims).filter(Zims.name == ziminfo.name).update({Zims.status: DOWNLOADING})
				session.commit()
				logging.info(f"trigger zim file: {ziminfo.name} status to {DOWNLOADING}")
				break
			else:
				logging.info(f"zim file: {ziminfo.name} status now is {ziminfo.status}")
				break
	except:
		session.rollback()
	finally:
		session.close()

if __name__ == '__main__':
	argv = sys.argv[1:]

	dbname = '/wiki/wiki.db'
	#parse args
	try:
		opts, args = getopt.getopt(argv, "d:", [
            "dbname="
        ])
	except:
		logging.error("parse arguments failed")
		sys.exit(-1)

	for opt, arg in opts:
		if opt in ['--dbname','-d']:
			dbname = arg

	#create new sqlite engine
	engine = create_engine(f"sqlite:///{dbname}?check_same_thread=False", echo=False)

	#create tables if not exists
	Base.metadata.create_all(engine, checkfirst=True)

	#create Session maker
	Session = sessionmaker(bind = engine)

	#start a thread to update zim list from dumps.wikimedia.org
	Thread(target = update_zim_dump_list).start()

	#trigger a zim file to uploading status
	while True:

		trigger_wiki_downloading()

		time.sleep(120)
