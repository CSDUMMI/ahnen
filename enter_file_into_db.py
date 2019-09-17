#! /bin/usr/python3.5


import sqlite3, sys, yaml, time

def create_file( title, description, date, imgs, folder_name, transcription, notes, cursor):
     """
A file:
title          : Descriptive title of a file or the actual title of the file
description    : Description of the file
img            : Path relative to ./imgs/<img>/ of the scanned file
folder_name    : Folder to find these in
transcription  : Transcription of the File ( might not be helpful or empty, if the file is a map or similar )
notes          : Notes to the file and additional information.
    """
     insertion_cmd = """
INSERT INTO files VALUES ( ?, ?, ?, ?, ?, ?, ? )
     """

     cursor.execute( insertion_cmd, [ date, description, title, imgs, folder_name, transcription, notes ] )

def write_all():

    connection = sqlite3.connect( 'ahnen.db' )

    cursor     = connection.cursor()

    for filename in sys.argv[1:]:
        file_ = open( filename ).read().split("\n")

        date          = file_.index('%date')
        title         = file_.index('%title') # Everything after this is the title
        description   = file_.index('%description')
        transcription = file_.index('%transcription')
        folder_name   = file_.index('%folder_name')
        img           = file_.index('%img')
        notes         = file_.index('%notes')

        date          = '\n'.join( file_[ date+1 : title ] )          # Only the lines of the date
        title         = '\n'.join( file_[ title+1 : description ] )
        description   = '\n'.join( file_[ description +1 : transcription ] )
        transcription = '\n'.join( file_[ transcription +1 : folder_name ] )
        folder_name   = '\n'.join( file_[ folder_name +1 : img ] )
        img           =   ''.join( file_[ img +1 : notes ] )
        notes         = '\n'.join( file_[ notes +1 : len( file_ ) ] )

        print (
            """
Date:
{}
Title:
{}
Description:
{}
Transcription:
{}
Folder Name:
{}
Images:
{}
Notes:
{}
            """.format( date, title, description, transcription, folder_name, img, notes )
            )
        create_file( title, description, date, img, folder_name, transcription, cursor )

        connection.commit()
    try:
        connection.close()
    except Exception as e:
        print(e)
    else:
        print( " Successfully wrote all files to db " )


if __name__ == '__main__':
     write_all()
