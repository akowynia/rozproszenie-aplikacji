import time
import logging
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
from .config import settings

logger = logging.getLogger(__name__)

hosts = [h.strip() for h in settings.cassandra_hosts.split(",")]

cluster = None
session = None

def get_session():
    global session
    if session is None:
        raise RuntimeError("Cassandra session is not initialized. Call init_db() first.")
    return session

def init_db():
    global cluster, session
    
    retries = 15
    delay = 5
    
    for i in range(retries):
        try:
            logger.info(f"Connecting to Cassandra (attempt {i+1}/{retries})...")
            cluster = Cluster(
                contact_points=hosts,
                port=settings.cassandra_port,
                load_balancing_policy=RoundRobinPolicy()
            )
            session = cluster.connect()
            break
        except Exception as e:
            logger.warning(f"Failed to connect to Cassandra: {e}. Retrying in {delay}s...")
            if cluster:
                try:
                    cluster.shutdown()
                except Exception:
                    pass
            time.sleep(delay)
    else:
        raise RuntimeError("Could not connect to Cassandra cluster after multiple retries.")

    session.execute(
        f"CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace} "
        "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};"
    )
    
    session.set_keyspace(settings.cassandra_keyspace)
    
    session.execute(
        "CREATE TABLE IF NOT EXISTS urls ("
        "  code text PRIMARY KEY,"
        "  original_url text,"
        "  created_at timestamp,"
        "  expires_at timestamp"
        ");"
    )
    logger.info("Cassandra database successfully initialized.")

def shutdown_db():
    global cluster, session
    if session:
        try:
            session.shutdown()
        except Exception:
            pass
    if cluster:
        try:
            cluster.shutdown()
        except Exception:
            pass
        logger.info("Cassandra connections closed.")
