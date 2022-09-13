from django.http import HttpResponse
import sqlalchemy, sqlite3, requests, re, datetime, json


HOST = 'https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/'
    
engine = sqlalchemy.create_engine('sqlite:///db.sqlite3')
connection = engine.connect()

def trigger(request):
    response = {}
    time_trigger = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Get the list of files
    res = requests.get(HOST)
    regexp = r'\>(wikipedia\S{1,}\.zim)\<\S{1,}\s{1,}(\S{1,}\s{1,}\S{1,})\s{1,}(\d{1,})'
    list_zim = re.findall(regexp, res.text)
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    for file in list_zim:
        name = file[0]
        timestamp = file[1]
        size = file[2]
        cursor.execute('SELECT * FROM zimfile_zimfile WHERE name=?', (name,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO zimfile_zimfile (name, timestamp, size, status) VALUES (?, ?, ?, ?)', (name, timestamp, size,'NEW'))
            conn.commit()
            response[name] = 'New file added'
        elif cursor.fetchone() is not None:
            cursor.execute('SELECT * FROM zimfile_zimfile WHERE name=?', (name,))
            row = cursor.fetchone()
            print(row)
            if row[1] != timestamp:
                cursor.execute('UPDATE zimfile_zimfile SET timestamp=?, size=?, status=? WHERE name=?', (timestamp, size, 'UPDATED', name))
                conn.commit()
                response[name] = 'File updated'
            elif row[2] == timestamp:
                response[name] = 'File already in database'
    conn.close()
    return HttpResponse(json.dumps({time_trigger: response}), content_type='application/json')  