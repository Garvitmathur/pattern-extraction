import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os;

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    

    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pattern_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pattern_class VARCHAR(255),
        pattern_instance VARCHAR(255),
        pattern_subclass VARCHAR(255),
        sheet_name VARCHAR(255),
        user VARCHAR(255),
        UNIQUE (pattern_class, pattern_instance)  
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS token_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        token_instance VARCHAR(255),
        token_class VARCHAR(255),
        token_subclass VARCHAR(255),
        case_type VARCHAR(255),  
        relationship_type_A_G VARCHAR(255),
        relationship_type_G_A VARCHAR(255),
        related_instance VARCHAR(255),
        related_instance_class VARCHAR(255),
        scope VARCHAR(255),
        user VARCHAR(255),
        UNIQUE (token_instance, token_class)  
    )
    """)

    conn.commit()
    conn.close()


def insert_pattern_config(pattern_class, data):
    conn = get_connection()
    cur = conn.cursor()
    

    sql = """
    INSERT IGNORE INTO pattern_config 
    (pattern_class, pattern_instance, pattern_subclass, sheet_name, user) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.executemany(sql, data)

    conn.commit()
    conn.close()


def insert_token_info(data):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT IGNORE INTO token_info 
    (token_instance, token_class, token_subclass, case_type, relationship_type_A_G, 
     relationship_type_G_A, related_instance, related_instance_class, scope, user) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.executemany(sql, data)

    conn.commit()
    conn.close()


def process_excel(file_path):
    xl = pd.ExcelFile(file_path)


    pattern_df = xl.parse(xl.sheet_names[0]).fillna("")
    
    
    pattern_df.rename(columns={
        "PatternName": "pattern_name",
        "PatternInstance": "pattern_instance",
        "PatternSubclass": "pattern_subclass"
    }, inplace=True)

    pattern_class = xl.sheet_names[0]

    
    if {'pattern_name', 'pattern_instance', 'pattern_subclass'}.issubset(pattern_df.columns):
        pattern_data = [
            (
                str(row['pattern_name']),
                str(row['pattern_instance']),
                str(row['pattern_subclass']),
                pattern_class,
                "SYS"
            )
            for _, row in pattern_df.iterrows()
        ]
        insert_pattern_config(pattern_class, pattern_data)
    else:
        print(" Pattern columns missing in Excel. Check column names!")

    
    token_df = xl.parse(xl.sheet_names[1]).fillna("")

    
    token_df.rename(columns={
        "TOKEN_INSTANCE": "token_instance",
        "TOKEN_CLASS": "token_class",
        "TOKEN_SUBCLASS": "token_subclass",
        "CASE": "case_type",
        "RELATIONSHIP_TYPE_A-G": "relationship_type_a_g",
        "RELATIONSHIP_TYPE_G-A": "relationship_type_g_a",
        "RELATED_INSTANCE": "related_instance",
        "RELATED_INSTANCE_CLASS": "related_instance_class",
        "SCOPE": "scope"
    }, inplace=True)

    
    if {'token_instance', 'token_class'}.issubset(token_df.columns):
        token_data = [
            (
                str(row['token_instance']),
                str(row['token_class']),
                str(row['token_subclass']),
                str(row['case_type']),
                str(row['relationship_type_a_g']),
                str(row['relationship_type_g_a']),
                str(row['related_instance']),
                str(row['related_instance_class']),
                str(row['scope']),
                "SYS"
            )
            for _, row in token_df.iterrows()
        ]
        insert_token_info(token_data)
    else:
        print(" Token columns missing in Excel. Check column names!")

    print(" Data inserted successfully into MySQL!")
