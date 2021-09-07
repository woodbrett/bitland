'''
Created on Nov 15, 2020

@author: brett_wood
'''

import psycopg2
from utilities.config import config


def executeSql (sql_statement):
    
    conn = None
    
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql_statement)
        # get the generated id back
        sql_return = cur.fetchall()[0]
        # commit the changes to the database
        conn.commit()
        # execute the UPDATE statement
        
        #print(parcel_id[0])
        #cur.execute(getUpdateParcelGeomSql(parcel_id[0]))
        
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql error: " + error)
    finally:
        if conn is not None:
            conn.close()

    return sql_return


def executeSqlMultipleRows (sql_statement):
    
    conn = None
    
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql_statement)
        # get the generated id back
        sql_return = cur.fetchall()
        # commit the changes to the database
        conn.commit()
        # execute the UPDATE statement
        
        #print(parcel_id[0])
        #cur.execute(getUpdateParcelGeomSql(parcel_id[0]))
        
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return sql_return


def executeSqlDeleteUpdate (sql_statement):
    
    conn = None
    
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql_statement)
        # get the number of updated rows
        rows_deleted = cur.rowcount
        # commit the changes to the database
        conn.commit()
        # execute the UPDATE statement
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted


def executeSqlInsert (sql_statement):
    
    conn = None
    
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql_statement)
        # get the number of updated rows
        rows_inserted = cur.rowcount
        # commit the changes to the database
        conn.commit()
        # execute the UPDATE statement
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_inserted


if __name__ == '__main__':
    print("hello")
    print(executeSql("select 1")[0])
    print(executeSql("select * from bitland.landbase_enum where valid_claim = true;"))
    