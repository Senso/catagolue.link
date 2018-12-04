import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import urllib.request
import sqlite3
import glob
import time
import re

today = time.strftime('%Y%m%d', time.gmtime(time.time()))

frontpage = ['b3s23/C1', 'b3s23/C2_1', 'b3s23/C4_1', 'b3s23/D8_1', 'b3s12/C1', 'b38s23/C1', 'b3s2-i34q/C1', 'b367s2-i34q/C1']

con = sqlite3.connect('catagolue.db')
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY, rule TEXT UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS objects (rule INTEGER, date TEXT, objcount INTEGER)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_objects ON objects(date, objcount)")

def scrape(rule):
    #cur.execute("SELECT id,rule FROM rules;")
    #for rule in cur.fetchall():
    fd = urllib.request.urlopen("https://catagolue.appspot.com/textcensus/%s/objcount" % rule[1])
    page = fd.read().decode('utf-8')
    cmatch = re.search('Total objects: ([0-9]+)', page)
    if cmatch:
        objcount = cmatch.group(1)
        cur.execute("INSERT INTO objects VALUES(?, ?, ?) ON CONFLICT(date, objcount) DO NOTHING", (rule[0], today, objcount))
        con.commit()

def filetorule(rule):
    rule = rule.replace('_', '/', 1)
    rule = rule.replace('catagolue/', '')
    rule = rule.replace('.dat', '')
    return rule

def ruletofile(rule):
    rule = rule.replace('/', '_')
    rule = rule.replace('catagolue/', '')
    return rule

def plot_graph(rule):
    cur.execute("select id from rules where rule=?", (rule,))
    rid = cur.fetchone()[0]
    cur.execute("SELECT date,max(objcount) from objects WHERE rule = ? group by date order by date asc", (rid,))
    results = cur.fetchall()

    xdata = [datetime.strptime(x[0], "%Y%m%d") for x in results]

    #plt.title(rule)
    fig, ax = plt.subplots()
    #plt.title(rule)
    ax.set_title(rule)
    ax.plot(xdata, [x[1] for x in results])
    ax.set_title(rule)
    #plt.title(rule)
    
    days = mdates.AutoDateLocator(maxticks=10, interval_multiples=False)
    fuckoff = mdates.DateFormatter('%Y-%m-%d')

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(fuckoff)
    fig.autofmt_xdate()

    plt.ylabel('objcount')
    plt.xlabel('date')
    
    filename = "/var/www/html/stats/%s.png" % ruletofile(rule)
    plt.savefig(filename, format='png')
    plt.close(fig)
    #plt.show()

def convert_oldstyle(file):
    rule = filetorule(file)

    cur.execute("insert into rules(rule) values(?) ON CONFLICT(rule) DO NOTHING", (rule,))
    con.commit()

    cur.execute("SELECT id from rules WHERE rule=?", (rule,))
    ruleid = cur.fetchone()[0]

    fd = open(file, 'r')
    for line in fd.read().split('\n'):
        ff = line.split(' ')
        if ff != ['']:
            cur.execute("INSERT INTO objects(rule, date, objcount) VALUES (?, ?, ?) ON CONFLICT(date, objcount) DO NOTHING", (ruleid, ff[0], ff[1]))
            con.commit()


def build_html():
    index = ''
    others = ''
    with open('header.html') as h:
        index += h.read()

        cur.execute("SELECT rule FROM rules;")
        for rule in cur.fetchall():
            filest = ruletofile(rule[0])

            if rule[0] in frontpage:
                
                index += '''
                <div style='float:left; overflow: hidden; text-align:center;'>
                <strong><a href="https://catagolue.appspot.com/census/%s" target="_blank">%s</a></strong> <br />
                <a href="%s.png">
                    <img src="%s.png" width=300 height=200>
                </a>
                </div>

                ''' % (rule[0], rule[0], filest, filest)
            else:
                others += '''
                <a href="%s.png">%s</a> <br />
                ''' % (filest, rule[0])

    index += "<div style='clear:both; width:100%;float:none;'>\n"
    index += "<br /> <br /><span>Other rules</span> <br /> \n"
    index += others
    index += "</div>\n"

    with open('footer.html') as f:
        index += f.read()

    with open('/var/www/html/stats/index.html', 'w') as ind:
        ind.write(index)

if __name__ == '__main__':
    cur.execute("SELECT id,rule FROM rules")
    for rule in cur.fetchall():
        scrape(rule)

        #for i in glob.glob("catagolue/*.dat"):
        #    convert_oldstyle(i)
        plot_graph(rule[1])

        build_html()














