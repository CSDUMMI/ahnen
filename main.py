#! /bin/usr/python3.5
from flask import Flask, request, render_template, send_from_directory, redirect, session
from Crypto.Hash import SHA256
from Crypto import Random
import sqlite3



app         = Flask(__name__, static_folder = 'static', static_url_path = '')

entry_key   = "85e4d47325acc8a12308c08b4499319da5866aca9343529d802a1ef7506c2272"

app.secret_key = Random.new().read(16)

def connect():
    return sqlite3.connect('ahnen.db')

@app.route("/")
def index():

    if not session.get( 'logged_in' ):
        return redirect( '/login' )
    
    connection  = connect()
    cursor      = connection.cursor()
    query       = "SELECT id, title, description FROM files"
    cursor.execute ( query )
    results     = cursor.fetchall()
    return render_template(
            "index.html",
            results = results
            )

@app.route("/files/<id>/")
def file(id):

    if not session.get( 'logged_in' ): # Check if logged in, otherwise go to /login
        return redirect( '/login' )

    
    connection      = connect()
    cursor          = connection.cursor()
    query           = "SELECT * FROM files WHERE id = ?"
    cursor.execute( query, [ id ] )

    results = cursor.fetchone()

    if not results:
        return render_template(
                    'error.html',
                    error       = "Not found",
                    description = "File not found"
                    )
    (
        date,
        description,
        title,
        imgs,
        folder_name,
        transcription,
        notes,
        id
    )               = results
    imgs = imgs.split(';')
    transcription = transcription.split('%page')
    try:
        transcription.remove('')
    except ValueError:
        pass
    
    for page in range( len( transcription ) ):
        page_text               = transcription[ page ].split('\n')
        page_title              = page_text[ 0 ]
        page_text               = '\n'.join( page_text [ 1: ] )
        transcription[ page ]   = ( page_title, page_text )

    return render_template(
                            'present_file.html',
                            date            = date,
                            description     = description,
                            title           = title,
                            imgs            = imgs,
                            folder_name     = folder_name,
                            transcription   = transcription,
                            notes           = notes,
                            id              = id
                          )

@app.route("/search")
def search():

    if not session.get( 'logged_in' ):
        return redirect( '/login' )

    
    places = {
        "date"          : "date",
        "description"   : "description",
        "title"         : "title",
        "img"           : "img",
        "folder_name"   : "folder_name",
        "transcription" : "transcription",
        "notes"         : "notes"
    }
    connection      = connect()
    cursor          = connection.cursor()
    search_query    = request.args.get('search')
    place           = places[ request.args.get('place') ] # ERROR if none of the accepted places
    query           = "SELECT title, description, id FROM files WHERE {} LIKE ?".format( place )
    cursor.execute( query, [ "%{}%".format( search_query ) ] )
    results         = cursor.fetchall()
    return render_template( 'search.html', results = results, query = search_query )

@app.route( "/login", methods = [ "GET" ] )
def login_page():
    return render_template( 'login.html' )

@app.route( "/login", methods = [ "POST" ] )
def login():
    if not session.get( 'logged_in' ):
        key  = request.values.get('key')
        hash = SHA256.new()
        hash.update( key.encode( 'utf-8' ) )
        
        if hash.hexdigest() == entry_key:
            session['logged_in'] = True
        else:
            session['logged_in'] = False
            return redirect ( '/login' )
    
    return redirect( '/' ) 

if __name__ == '__main__':
    app.run(host="0.0.0.0")
