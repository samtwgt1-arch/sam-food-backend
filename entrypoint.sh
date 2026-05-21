#!/bin/bash
# Copy pre-seeded ChromaDB data to ephemeral /tmp
if [ ! -f "/tmp/chromadb_data/chroma.sqlite3" ]; then
    echo "Initializing ChromaDB from embedded data..."
    cp -r /app/chromadb_data /tmp/chromadb_data
    echo "ChromaDB initialized."
else
    echo "ChromaDB data already exists."
fi

exec "$@"