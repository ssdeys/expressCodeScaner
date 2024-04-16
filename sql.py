import pymysql
from pymysql import Error

class BarcodeDatabase:
    def __init__(self, host, user, password, dbname):
        """Constructor to set up the database connection."""
        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          password=password,
                                          database=dbname)
        self.cursor = self.connection.cursor()

    def insert_barcode_data(self, danhao, photo_path,riqi,charushijian):
        """Insert barcode data and photo into the database."""
        try:
            with open(photo_path, 'rb') as photo_file:
                photo_data = photo_file.read()
            
            query = "INSERT INTO danhao (danhao, photo,riqi,charushijian) VALUES (%s, %s,%s,%s)"
            self.cursor.execute(query, (danhao, photo_data,riqi,charushijian))
            self.connection.commit()
            print("Data inserted successfully.")
        except Error as e:
            print(f"Error inserting data: {e}")
        except FileNotFoundError:
            print(f"File {photo_path} not found.")
    
    def get_all_data(self):
        """Retrieve all barcode data from the database."""
        try:
            query = "SELECT danhao, photo,paisong,dizhi,riqi,charushijian FROM danhao"
            self.cursor.execute(query)
            return [(danhao, photo,paisong,dizhi,riqi,charushijian) for danhao, photo,paisong,dizhi,riqi,charushijian in self.cursor.fetchall()]  # 获取所有记录，不要解码
        except pymysql.Error as e:
            print(f"Error retrieving data: {e}")
            return None

    
       

    def close(self):
        """Close the database connection."""
        self.connection.close()

# Usage example
# db = BarcodeDatabase('localhost', 'username', 'password', 'database_name')
# db.insert_barcode_data('123456789', '/path/to/photo.jpg')
# db.close()