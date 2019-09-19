#! /bin/usr/python3.5
from flask import Flask, request, render_template, send_from_directory
import sqlite3



app         = Flask(__name__, static_folder = 'static', static_url_path = '')

def connect():
    return sqlite3.connect('ahnen.db')

@app.route("/")
def index():
    connection  = connect()
    cursor      = connection.cursor()
    query       = "SELECT id, title, description FROM files"
    cursor.execute ( query )
    results     = cursor.fetchall()
    return render_template(
            "index.html",
            results = results
            )

@app.route("/files/<id>")
def file(id):
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

if __name__ == '__main__':
    app.run(host="0.0.0.0")
