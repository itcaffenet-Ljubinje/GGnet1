#!/bin/bash
set -e

# Database Setup Script for ggNet

echo "=================================="
echo "ggNet Database Setup"
echo "=================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Check PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL is not running. Start it first:"
    echo "   sudo systemctl start postgresql"
    exit 1
fi

# Create user and database
echo "📋 Creating database user and database..."
sudo -u postgres psql << EOF
-- Create user
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ggnet') THEN
        CREATE USER ggnet WITH PASSWORD 'ggnet123';
        RAISE NOTICE 'User ggnet created';
    ELSE
        RAISE NOTICE 'User ggnet already exists';
    END IF;
END
\$\$;

-- Create database
SELECT 'CREATE DATABASE ggnet OWNER ggnet'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ggnet')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;

\c ggnet
GRANT ALL ON SCHEMA public TO ggnet;
EOF

echo "✅ Database setup complete"
echo
echo "Database details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: ggnet"
echo "  User: ggnet"
echo "  Password: ggnet123 (change this in production!)"
echo
echo "Test connection:"
echo "  psql -h localhost -U ggnet -d ggnet"
echo

