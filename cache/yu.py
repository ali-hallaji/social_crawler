import csv
#class to provide utility for extracting csv data
#upon creating a CsvFile object you must call .fill() to fill the data
import csv

class CsvFile(object):


    def __init__(self, name):
        self.name = name
        self.data = []
        self.columns = []
    def __str__(self):
        return self.name

    def empty(self):
        self.data = []

    def fill(self):
        import csv
        self.data = [x for x in csv.DictReader(open(self.name, 'rU'))]
        self.columns = self.data[0].keys()


def find_all_types(data, key, index=1, types ='VARCHAR'):

    dlist = [x[key] for x in data]
    try:
        intlist = [int(x) for x in dlist]

        return 'INT'
    except ValueError:  
        try:
            floatlist = [float(x) for x in dlist]

            return 'DECIMAL'
        except ValueError:
            return 'VARCHAR'


def find_type(csv_object, padding = 3):
    csv_object = CsvFile(csv_object)
    csv_object.fill()
    data = csv_object.data
    columns = csv_object.columns
    master_type = {columns[x]:find_all_types(data, list(data[1].keys())[x])for x in xrange(len(columns))}
    master_len = {columns[x]:1 for x in xrange(len(columns))}
    for x in data:
        for k, v in x.iteritems():
            if len(v) > master_len[k]:
                master_len[k] = len(v)

    master_len = {k:(v+padding) for k, v in master_len.iteritems() }

    return master_len, master_type

def build_sql(csv_object, tablename='SampleTable', decimalplace = 2, padding =3):
    mlen, mtype =find_type(csv_object, padding)

    rebuild = {k.replace(" ","_"):(  mtype[k] +'(65)'   ) for k in mlen.keys()}
    for k, v in rebuild.iteritems():
        if v.startswith('DECIMAL'):
            rebuild[k] = v[:-1] +',' + str(decimalplace) +')'

    sql = 'CREATE TABLE ' + str(tablename) + '\n' + '(' 
    for k, v in rebuild.iteritems():
        sql +=  '\n' +str(k) +" " +str(v) +','
    sql = sql[:-1]
    sql += '\n' +');'
    return sql 

#--------------------------------------------------------
#EXAMPLE USAGE
#Padding is added to the max length of each field to arrive at the total length for each field used in the create table statement

