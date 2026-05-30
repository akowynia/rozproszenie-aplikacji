import time
import logging
from datetime import datetime, timezone
from app.config import settings
from app.database import init_db, get_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cleanup")

def run_cleanup():
    if not settings.cleanup_enabled:
        return
    
    try:
        session = get_session()
    except Exception as e:
        logger.error(f"Cannot get active database session: {e}")
        return

    try:
        query = "SELECT code, created_at, last_used_at FROM urls"
        rows = session.execute(query)
    except Exception as e:
        logger.error(f"Error fetching entries from database: {e}")
        return

    now = datetime.now(timezone.utc)
    deleted_count = 0

    for row in rows:
        code = row.code
        created_at = row.created_at
        last_used_at = row.last_used_at

        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if last_used_at and last_used_at.tzinfo is None:
            last_used_at = last_used_at.replace(tzinfo=timezone.utc)

        target_time = created_at
        if settings.cleanup_strategy == "last_used_at":
            target_time = last_used_at or created_at

        if not target_time:
            continue

        age_seconds = (now - target_time).total_seconds()
        
        if age_seconds > settings.cleanup_ttl_seconds:
            logger.info(f"[EXPIRED] Code '{code}' (created: {created_at}, last used: {last_used_at}, age: {age_seconds:.1f}s) - DELETING")
            try:
                delete_query = "DELETE FROM urls WHERE code = %s"
                session.execute(delete_query, (code,))
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete code '{code}': {e}")

    if deleted_count > 0:
        logger.info(f"Cleanup cycle finished. Deleted {deleted_count} expired entries.")

def main():
    logger.info("Initializing Cleanup Service...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return

    while True:
        try:
            run_cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup execution: {e}")
        
        time.sleep(settings.cleanup_interval_seconds)

if __name__ == "__main__":
    main()
