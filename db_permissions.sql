--platform_admin
ALTER DATABASE platform_dev_db OWNER TO platform_admin;
ALTER SCHEMA public OWNER TO platform_admin;

--platform_dev
GRANT CONNECT ON DATABASE platform_dev_db TO platform_dev;
GRANT USAGE ON SCHEMA public TO platform_dev;
GRANT CREATE ON SCHEMA public TO platform_dev;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO platform_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO platform_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO platform_dev;