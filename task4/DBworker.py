from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


class DbConfig:
    def read_db_config(self, filename='config.ini', section='mysql'):
        parser = ConfigParser()

        parser.read(filename)
        db = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, filename))

        return db


class DbWorker:
    def __init__(self, configpath):
        self.configpath = configpath
        self.queriesdict = {
            'get_all_students': 'SELECT r.* , s.StudentID  id, s.StudentName  name, s.StudentSex  sex'
                                ' FROM rooms r, students s WHERE r.RoomNumber = s.StudentRoomNumber ;',
            'get_students_count': """
                SELECT r.RoomName, COUNT(students.StudentID)
                AS total FROM rooms r 
                LEFT JOIN students ON r.RoomNumber = students.StudentRoomNumber 
                GROUP BY r.RoomName
                """,
            'get_top5_avg_age': """
                SELECT rooms.RoomName
                AS total FROM rooms
                LEFT JOIN students ON rooms.RoomNumber=students.StudentRoomNumber GROUP BY rooms.RoomName
                ORDER BY -AVG(students.StudentBirthday) limit 6
                """,
            'get_top5_max_diff_in_age': """
                SELECT rooms.RoomName
                FROM rooms LEFT JOIN students ON rooms.RoomNumber=students.StudentRoomNumber 
                GROUP BY rooms.RoomName 
                ORDER BY DATEDIFF(MIN(students.StudentBirthday),
                MAX(students.StudentBirthday)) LIMIT 6;
                """,
            'get_rooms_with_diff_sex': """
                SELECT rooms.RoomName AS total FROM rooms 
                JOIN students ON rooms.RoomNumber=students.StudentRoomNumber  
                GROUP BY rooms.RoomName
                HAVING COUNT(DISTINCT students.StudentSEX)>1;
                """
        }

    def __enter__(self):

        self.db_config = DbConfig().read_db_config(filename=self.configpath)

        try:
            print('Connecting to MySQL database...')
            self.conn = MySQLConnection(**self.db_config)
            if self.conn.is_connected():
                print('connection established.')
            else:
                print('connection failed.')
            self.cursor = self.conn.cursor()

        except Error as error:
            print(error)

    def insert_students(self, students: list):
        for stud in students:
            self.cursor.execute('INSERT INTO students (StudentID, RoomNumber, '
                                'StudentName, StudentBirthday, StudentSEX) '
                                'VALUES  (%s, %s, %s, %s, %s)',
                                (stud.id, stud.room, stud.name, stud.birthday, stud.sex))
        self.conn.commit()

    def insert_rooms(self, rooms: list):
        for room in rooms:
            self.cursor.execute('INSERT INTO rooms (RoomID, RoomName, RoomNumber) VALUES (%s, %s, %s)',
                                (room.id, room.name, room.number))
        self.conn.commit()

    def execute_queries(self, outputformat, Writer):
        writer = Writer().choose_format(outputformat)
        for key in self.queriesdict:
            self.cursor.execute(self.queriesdict[key])
            writer.writefile(key, self.cursor.fetchall())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print('Connection closed.')


class IndexWorker:
    def __init__(self, connector: MySQLConnection):
        self.conn = connector
        self.cursor = connector.cursor()

    def birth_index(self):
        query = 'CREATE INDEX age ON students(StudentBirthday)'
        self.cursor.execute(query)
        self.conn.commit()

    def room_index(self):
        query = 'CREATE INDEX room_number ON students(StudentRoomNumber)'
        self.cursor.execute(query)
        self.conn.commit()