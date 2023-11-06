'''
The majority of this code was written by @rafrafraf, my old coding partner who is busy fighting for his country.

The code has been **very** slightly modified by me (@MarcusWeinberger) to make it work again although not all of it may be functional. 

I've had to migrate database host, and sadly the new host is signifigantly slower.
'''
from flask import Flask, jsonify, request, render_template, redirect, session
from flask_cors import CORS
from sqlalchemy import create_engine
import os, datetime, sqlalchemy
import pymysql

pymysql.install_as_MySQLdb()

class ReplDBSQL(object):
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self.engine = create_engine(db_uri, pool_size=5, pool_recycle=3600)

    def run(self, query: str, vals: dict={}):
        conn = self.engine.connect()
        query = conn.execute(sqlalchemy.text(query), **vals)
        try:
            res = query.fetchall()
        except:
            res = None
        conn.commit()
        conn.close()
        if res:
            return [row._mapping for row in res]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# these two should speed up jsonify
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

CORS(app)
db = ReplDBSQL(os.getenv("DB_URI"))

db.run('''
CREATE TABLE IF NOT EXISTS hits (
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    Domain TEXT NOT NULL,
    Route TEXT NOT NULL,
    Timestamp INTEGER NOT NULL,
    Browser TEXT,
    Location TEXT,
    Device TEXT,
    Referrer TEXT
)
''')

db.run('''
CREATE TABLE IF NOT EXISTS domains (
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    Domain TEXT NOT NULL,
    User TEXT
)
''')


@app.route('/')
def app_index():
    return redirect('https://analytics.marcusj.org/analytics.marcusj.org')

@app.route('/<domain>')
def app_get(domain):
    return render_template('base.html', home=(domain == 'analytics.marcusj.org'))

@app.route('/getAllVisits/<domain>')
def getAllVisits(domain):
    visits = db.run('SELECT COUNT(CASE WHEN Domain != Referrer THEN 1 END) as visits FROM hits WHERE Domain = :domain;', {'domain':domain})

    return jsonify({'visits':visits})

@app.route('/daterange', methods=['GET'])
def daterange():
    data = dict(request.args or request.json or request.get_json() or request.form)
    domain = data['domain']
    d1 = int(data['d1'])
    d2 = int(data['d2'])

    check = db.run('SELECT * FROM domains WHERE Domain = :domain;', {'domain':domain})

    if len(check) == 0:
        return jsonify({'status':404, 'message':'domain not found'})
    
    graph = db.run('SELECT Timestamp, COUNT(ID) AS views, COUNT(CASE WHEN Domain != Referrer THEN 1 END) AS visits FROM hits WHERE Domain = :domain AND Timestamp BETWEEN :ts1 AND :ts2 GROUP BY Timestamp', {'domain':domain, 'ts1':d1, 'ts2':d2})

    info = db.run('SELECT Route, Browser, Location, Device, Referrer, COUNT(*) as Counter FROM hits WHERE Domain = :domain AND Timestamp BETWEEN :ts1 AND :ts2 GROUP BY Route, Browser, Location, Device, Referrer', {'domain':domain, 'ts1':d1, 'ts2':d2})

    return jsonify({'status':200, 'graph':graph, 'info':info})

@app.route('/analytics.js')
def app_analytics():
    #return "console.log('RIP dupl analytics')"
    return render_template('analytics.js')

@app.route('/setsession', methods=['POST'])
def app_setsession():
    session['user'] = request.form['user']
    session['user_id'] = request.form['user_id']
    return redirect(request.form.get('callback', 'https://analytics.marcusj.org/analytics.marcusj.org'))

@app.route('/clearsession')
def app_clearsession():
    session.clear()
    return redirect(request.args.get('callback', 'https://analytics.marcusj.org/analytics.marcusj.org'))

@app.route('/tos')
def app_tos():
    return 'coming soon'
@app.route('/privacy')
def app_privacy():
    return 'coming soon'

@app.route('/api/hit', methods=['POST'])
def api_hit():
    data = dict(request.json or request.get_json() or request.form)
    if db.run('SELECT Domain FROM domains WHERE Domain = :domain LIMIT 1', {'domain': data['Domain']}) == []:
        db.run('INSERT INTO domains (Domain) VALUES (:domain)', {'domain': data['Domain']})
    db.run('INSERT INTO hits (Domain, Route, Timestamp, Browser, Location, Device, Referrer) VALUES (:domain, :route, :ts, :browser, :loc, :device, :ref)', {
        'domain': data['Domain'],
        'route': data['Route'],
        'ts': datetime.datetime.now().replace(minute=0, second=0, microsecond=0).timestamp(),
        'browser': data.get('Browser'),
        'loc': data.get('Location'),
        'device': data.get('Device'),
        'ref': data.get('Referrer')
    })
    return 'ok'

@app.route('/api/<domain>/query', methods=['POST'])
def api_domain_query(domain):
    valid_keys = ['ID', 'Route', 'Timestamp', 'Browser', 'Location', 'Device', 'Referrer']
    valid_operaters = ['=', '>=', '<=', '!=']
    queries = request.json or request.get_json() or []
    query_list = []
    values = {}
    for q in queries:
        try:
            if q['key'] in valid_keys and q['op'] in valid_operaters:
                query_list.append(f'{q["key"]} {q["op"]} :v{len(values)}')
                values[f'v{len(values)}'] = q['val']
        except Exception as e:
            print(f'[!] err formatting query: {e}. Query: {q}')
    query_string = ' AND '.join(query_list)
    query = 'SELECT * FROM hits WHERE Domain = :domain' + (' AND ' if not values == {} else '') + query_string
    res = db.run(query, {'domain': domain, **values})
    return jsonify(res)

@app.route('/api/getdomains')
def api_getdomains():
    doms = db.run('SELECT DISTINCT Domain FROM hits')
    return jsonify({'domains': doms})