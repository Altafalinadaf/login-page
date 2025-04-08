import sqlite3
from sqlite3 import Error

def create_connection():
    """ Create a database connection to SQLite database """
    conn = None
    try:
        conn = sqlite3.connect('soil_crop.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create tables for soil types and crop recommendations """
    try:
        cursor = conn.cursor()
        
        # Soil properties table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS soil_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ph_min REAL NOT NULL,
            ph_max REAL NOT NULL,
            nitrogen_min REAL NOT NULL,
            nitrogen_max REAL NOT NULL,
            phosphorus_min REAL NOT NULL,
            phosphorus_max REAL NOT NULL,
            potassium_min REAL NOT NULL,
            potassium_max REAL NOT NULL,
            texture TEXT NOT NULL,
            drainage TEXT NOT NULL
        )
        """)
        
        # Crop recommendations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            soil_type_id INTEGER NOT NULL,
            optimal_ph_min REAL NOT NULL,
            optimal_ph_max REAL NOT NULL,
            nitrogen_needs TEXT NOT NULL,
            phosphorus_needs TEXT NOT NULL,
            potassium_needs TEXT NOT NULL,
            water_requirements TEXT NOT NULL,
            FOREIGN KEY (soil_type_id) REFERENCES soil_properties (id)
        )
        """)
        
        conn.commit()
    except Error as e:
        print(e)

def initialize_database():
    """ Initialize the database with sample data """
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        
        # Check if data already exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM soil_properties")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Insert sample soil types
        soils = [
            ('Sandy', 5.5, 7.5, 0.1, 0.3, 10, 30, 50, 100, 'Coarse', 'Fast'),
            ('Clay', 6.0, 7.5, 0.2, 0.5, 20, 50, 100, 200, 'Fine', 'Slow'),
            ('Loamy', 6.0, 7.0, 0.3, 0.6, 30, 60, 150, 300, 'Medium', 'Moderate'),
            ('Silty', 6.5, 7.5, 0.2, 0.4, 25, 50, 120, 250, 'Medium', 'Moderate'),
            ('Peaty', 3.5, 6.0, 0.4, 0.8, 15, 40, 80, 180, 'Organic', 'Slow')
        ]
        
        cursor.executemany("""
        INSERT INTO soil_properties 
        (name, ph_min, ph_max, nitrogen_min, nitrogen_max, phosphorus_min, phosphorus_max, 
         potassium_min, potassium_max, texture, drainage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, soils)
        
        # Insert sample crops
        crops = [
            # Sandy soil crops
            ('Carrots', 1, 6.0, 6.8, 'Medium', 'Medium', 'High', 'Moderate'),
            ('Radishes', 1, 6.0, 7.0, 'High', 'Medium', 'Medium', 'Moderate'),
            ('Potatoes', 1, 5.0, 6.0, 'High', 'High', 'High', 'High'),
            
            # Clay soil crops
            ('Cabbage', 2, 6.5, 7.5, 'High', 'High', 'High', 'High'),
            ('Broccoli', 2, 6.0, 7.0, 'High', 'High', 'High', 'High'),
            ('Brussels Sprouts', 2, 6.0, 7.5, 'High', 'High', 'High', 'High'),
            
            # Loamy soil crops
            ('Tomatoes', 3, 5.5, 7.0, 'High', 'High', 'High', 'Moderate'),
            ('Corn', 3, 5.8, 7.0, 'High', 'High', 'High', 'Moderate'),
            ('Beans', 3, 6.0, 7.0, 'Medium', 'Medium', 'Medium', 'Moderate'),
            
            # Silty soil crops
            ('Wheat', 4, 6.0, 7.0, 'Medium', 'High', 'Medium', 'Moderate'),
            ('Barley', 4, 6.0, 7.0, 'Medium', 'Medium', 'Medium', 'Moderate'),
            ('Oats', 4, 6.0, 7.0, 'Medium', 'Medium', 'Medium', 'Moderate'),
            
            # Peaty soil crops
            ('Blueberries', 5, 4.0, 5.0, 'Low', 'Medium', 'Medium', 'High'),
            ('Cranberries', 5, 4.0, 5.5, 'Low', 'Medium', 'Medium', 'High'),
            ('Potatoes', 5, 4.5, 6.0, 'High', 'High', 'High', 'High')
        ]
        
        cursor.executemany("""
        INSERT INTO crop_recommendations 
        (crop_name, soil_type_id, optimal_ph_min, optimal_ph_max, 
         nitrogen_needs, phosphorus_needs, potassium_needs, water_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, crops)
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    initialize_database()