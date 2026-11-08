-- Hindsight 使用独立数据库，避免与业务表混在一起
SELECT 'CREATE DATABASE hindsight'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'hindsight')\gexec
