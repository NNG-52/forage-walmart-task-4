import csv
import sqlite3
from collections import defaultdict

TABLE_NAME = "shipments"

def create_table(conn):
    """
    Create the table if it does not already exist.
    Adjust columns based on your CSV columns.
    """
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin_warehouse TEXT,
            destination_store TEXT,
            product TEXT,
            on_time boolean,
            quantity INTEGER,
            driver_identifier TEXT
        );
    """)
    conn.commit()

def insert_row(conn, row):
    """
    Insert a single CSV row (list of values) into the database.
    Adjust number of ? placeholders to match columns.
    """
    conn.execute(
        f"INSERT INTO {TABLE_NAME} (origin_warehouse, destination_store, product, on_time, quantity, driver_identifier) VALUES (?, ?, ?, ?, ?, ?);",
        row
    )


def load_data(file):
    
    with open(file, newline="") as f:
        reader = csv.DictReader(f)
        header = next(reader)   # Skip header row
    return reader  # Return a set of unique values from the specified column



def main():
    shipment_connector = sqlite3.connect("shipment_database.db")
    create_table(shipment_connector)

    try:
        with open('./data/shipping_data_0.csv', newline="") as csvfile:
            shipping_reader_0 = csv.reader(csvfile)
            header0 = next(shipping_reader_0)   # Skip header row
            for row in shipping_reader_0:
                insert_row(shipment_connector, row)
    except FileNotFoundError:
        print("Error: shipping_data_0.csv not found.")
    except Exception as e:
        print("Unexpected error:", e)


    csvfile1 = open('./data/shipping_data_1.csv', newline="") 
    shipping_reader_1 = csv.reader(csvfile1)
    header1 = next(shipping_reader_1)   # Skip header row

    csvfile2 = open('./data/shipping_data_2.csv', newline="") 
    shipping_reader_2 = csv.reader(csvfile2)
    header2 = next(shipping_reader_2)   # Skip header row 



    counts = defaultdict(int) # number of duplicates 
    prev1_tuple = tuple()
    prev2_tuple = tuple()
    entry = []
    for row in shipping_reader_1: # iterate each row through shipping_data_1  
        row1_tuple = tuple(row)
        
        if len(prev1_tuple) == 0: # first iteration
            prev1_tuple = row1_tuple
            counts[row1_tuple] = 1 
            continue


        if (row1_tuple == prev1_tuple):
            counts[prev1_tuple] += 1              
        else:
            if len(prev2_tuple) != 0: # second iteration
                if prev2_tuple[0] == prev1_tuple[0]:    
                    entry = [
                        prev2_tuple[1], # origin_warehouse
                        prev2_tuple[2], # destination_store
                        prev1_tuple[1], # product
                        prev1_tuple[2], # on_time
                        counts[prev1_tuple], # quantity
                        prev2_tuple[3] # driver_identifier
                    ] # Constructing the entry  each time we find a match
                    
                    counts[row1_tuple] = 1  # Reset count for new entry
                    prev1_tuple = row1_tuple
                    insert_row(shipment_connector, entry)
                    # print(entry)
                    continue
            for row2 in shipping_reader_2:
                row2_tuple = tuple(row2)

                if row2_tuple[0] == prev1_tuple[0]:                       
                    entry = [
                        row2_tuple[1], # origin_warehouse
                        row2_tuple[2], # destination_store
                        prev1_tuple[1], # product
                        prev1_tuple[2], # on_time
                        counts[prev1_tuple], # quantity
                        row2_tuple[3] # driver_identifier
                    ] # Constructing the entry  each time we find a match
                       
                    counts[row1_tuple] = 1  # Reset count for new entry
                    prev1_tuple = row1_tuple
                    prev2_tuple = row2_tuple
                    break              

            insert_row(shipment_connector, entry)
            # print(entry)
      

    shipment_connector.commit()
    shipment_connector.close()
    csvfile1.close()
    csvfile2.close()

    print("CSV data inserted into SQLite database successfully!")

  
if __name__ == "__main__":
    main()