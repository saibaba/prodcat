
from neo4j import GraphDatabase
import atexit

folder_to_put_db_in="database"
# Create a database
db = GraphDatabase(folder_to_put_db_in)
# install shutdown hook to shutdown database
atexit.register(lambda : db.shutdown() )

