import pyorient

def connect():
        client = pyorient.OrientDB("localhost", 2424)
        session_id = client.connect( "root", "rootlabs" )
        client.db_open( "NetworkLabs", "admin", "admin")
        return client
