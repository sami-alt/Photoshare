'''Module providing sqlite3'''
import sqlite3
from flask import g

def get_connection():
    '''Create connection to databae'''
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params):
    ''' Execute queries '''
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    '''
    Docstring for last_insert_id
    '''
    return g.last_insert_id

def query(sql, params, return_one=True):
    '''
    Docstring for query
    
    :param sql: Description
    :param params: Description
    '''
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result[0] if return_one else result
