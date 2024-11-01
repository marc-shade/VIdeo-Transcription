import sqlite3
from datetime import datetime
import os

class TranscriptionDB:
    def __init__(self, db_name='transcription.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Create a database connection with foreign key support enabled."""
        conn = sqlite3.connect(self.db_name)
        conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support for all connections
        return conn

    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create clients table with name field
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create transcriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            transcription_text TEXT NOT NULL,
            include_timestamps BOOLEAN NOT NULL,
            target_language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
            ON DELETE CASCADE
        )
        ''')

        conn.commit()
        conn.close()

    def add_client(self, name, email):
        """Add a new client to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO clients (name, email) VALUES (?, ?)', (name, email))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # If email already exists, update the name
            cursor.execute('UPDATE clients SET name = ? WHERE email = ?', (name, email))
            cursor.execute('SELECT id FROM clients WHERE email = ?', (email,))
            conn.commit()
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def update_client(self, client_id, name, email):
        """Update client information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE clients SET name = ?, email = ? WHERE id = ?', 
                         (name, email, client_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_client(self, client_id):
        """Delete a client and all their associated transcriptions."""
        conn = self.get_connection()
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        try:
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            # Delete transcriptions first
            cursor.execute('DELETE FROM transcriptions WHERE client_id = ?', (client_id,))
            # Then delete the client
            cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
            # Commit transaction
            conn.commit()
            return True
        except Exception as e:
            # Rollback in case of error
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_all_clients(self):
        """Get all clients."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name, email, created_at FROM clients ORDER BY name')
            return cursor.fetchall()
        finally:
            conn.close()

    def get_client_by_id(self, client_id):
        """Get client by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name, email, created_at FROM clients WHERE id = ?', 
                         (client_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_transcription(self, client_id, original_filename, transcription_text, 
                         include_timestamps, target_language=None):
        """Add a new transcription record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO transcriptions 
            (client_id, original_filename, transcription_text, include_timestamps, target_language)
            VALUES (?, ?, ?, ?, ?)
            ''', (client_id, original_filename, transcription_text, include_timestamps, target_language))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def delete_transcription(self, transcription_id):
        """Delete a transcription record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM transcriptions WHERE id = ?', (transcription_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_transcription_metadata(self, transcription_id, target_language):
        """Update transcription metadata."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE transcriptions 
            SET target_language = ?
            WHERE id = ?
            ''', (target_language if target_language != "Original" else None, transcription_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_client_transcriptions(self, client_id=None, email=None):
        """Get all transcriptions for a client by ID or email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if client_id:
                cursor.execute('''
                SELECT t.* FROM transcriptions t
                WHERE t.client_id = ?
                ORDER BY t.created_at DESC
                ''', (client_id,))
            else:
                cursor.execute('''
                SELECT t.* FROM transcriptions t
                JOIN clients c ON t.client_id = c.id
                WHERE c.email = ?
                ORDER BY t.created_at DESC
                ''', (email,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_transcription(self, transcription_id):
        """Get a specific transcription by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM transcriptions WHERE id = ?', (transcription_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_all_client_transcriptions_text(self, client_id):
        """Get all transcriptions text for a client for bulk export."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT original_filename, transcription_text, target_language, created_at 
            FROM transcriptions 
            WHERE client_id = ?
            ORDER BY created_at
            ''', (client_id,))
            return cursor.fetchall()
        finally:
            conn.close()
