import pyorient

def connect():
        client = pyorient.OrientDB("localhost", 2424)
        session_id = client.connect( "root", "root" )
        client.db_open( "NetworkLabs", "admin", "admin")
        return client

