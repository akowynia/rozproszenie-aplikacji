from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    base_url: str = "http://localhost:8000"
    default_ttl_seconds: int = 86400
    max_ttl_seconds: int = 2592000
    short_code_length: int = 6
    cleanup_interval_seconds: int = 300
    cleanup_strategy: str = "created_at"
    cleanup_ttl_seconds: int = 31536000
    cleanup_enabled: bool = True
    cassandra_hosts: str = "localhost"
    cassandra_port: int = 9042
    cassandra_keyspace: str = "url_shortener"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "forbidden-urls-alerts"
    forbidden_words: str = "spam,phishing,malware,xxx,porn,gamble,scam,kurw,chuj,pierdol,jeb,cip,pizd"
    block_forbidden_urls: bool = False



settings = Settings()
