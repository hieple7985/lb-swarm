import requests
import sqlite3
import re
import  time

# url to get zim file
HOST = "https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/"

list_name_file = []

# connect database
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("SELECT * FROM zim_status")
rows = cursor.fetchall()
for row in rows:
    name_file = row[1]
    list_name_file.append(name_file)


# parse timestamp 
def parse_timestamp(timestamp, timeformat = '%d-%b-%Y %H:%M'):

	t = time.strptime(timestamp, timeformat)

	return int(time.mktime(t))

# parse size zim file
# def parse_size(size = 0.0):

# 	if size < 1024:
# 		return '{0} B'.format(round(size, 2))
# 	else:
# 		size /= 1024.0

# 	if size < 1024.0:
# 		return '{0} KB'.format(round(size, 2))
# 	else:
# 		size /= 1024.0

# 	if size < 1024:
# 		return '{0} MB'.format(round(size, 2))
# 	else:
# 		size /= 1024.0

# 	if size < 1024:
# 		return '{0} GB'.format(round(size, 2))
# 	else:
# 		size /= 1024.0

# 	if size < 1024:
# 		return '{0} TB'.format(round(size, 2))
# 	else:
# 		size /= 1024.0		

# 	return '{0} PB'.format(round(size, 2))

# send request to get all zime file name,zise, timestamp
res = requests.get(HOST)

if res.status_code >= 200 and res.status_code < 300:
    regexp = r'\>(wikipedia\S{1,}\.zim)\<\S{1,}\s{1,}(\S{1,}\s{1,}\S{1,})\s{1,}(\d{1,})'
    list_zim =  re.findall(regexp, res.text)

# save all zim prop to database    
for zim in list_zim:
    zim_name = zim[0]
    zim_size = int(zim[2])
    zim_timestamp = parse_timestamp(zim[1])

    if zim_name not in list_name_file:
        insert = '''
                INSERT INTO zim_status (name,size,timestamp,status) VALUES ('{}','{}','{}','waiting_download')
                '''.format(zim_name,zim_size,zim_timestamp)

        cursor.execute(insert)
    
conn.commit()

cursor.execute("SELECT * FROM zim_status")
rows = cursor.fetchall()
print("...")
for row in rows[-10:]:
    print(row)
print("...")   
    
conn.close

