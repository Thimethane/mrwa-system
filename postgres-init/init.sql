-- ============================================================================
-- MRWA PostgreSQL Initialization Script
-- ============================================================================

-- Create user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = '${POSTGRES_USER}'
   ) THEN
      CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';
   END IF;
END
$do$;

-- Create database if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = '${DATABASE_NAME}'
   ) THEN
      CREATE DATABASE ${DATABASE_NAME} OWNER ${POSTGRES_USER};
   END IF;
END
$do$;
