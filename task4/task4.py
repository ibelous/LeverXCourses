import json
import xml.etree.cElementTree as ET
import argparse
import datetime
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


class Student:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.name = data.get('name')
        self.room = data.get('room')
        self.birthday = data.get('birthday')
        self.sex = data.get('sex')

    def __str__(self):
        return 'id: {}, name: {}, birthday: {}, sex: {}, room: {}'.\
            format(self.id, self.name, self.birthday, self.sex, self.room)

    def __repr__(self):
        return '\nid: {}, name: {}, birthday: {}, sex: {}, room: {}'. \
            format(self.id, self.name, self.birthday, self.sex, self.room)


class Room:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.name = data.get('name')
        self.number = int(self.name[6:])

    def __str__(self):
        return 'id: {}, name: {}, number: {}'.format(self.id, self.name, self.number)


class RoomWithStudents(Room):
    def __init__(self, data: dict):
        super().__init__(data=data)
        self.students = []

    def __str__(self):
        return 'id: {}, name: {}, number: {}, students: {}'.format(self.id, self.name, self.number,
                                                                   self.students)

    def __repr__(self):
        return 'id: {}, name: {}, number: {}, students: {}'.format(self.id, self.name, self.number,
                                                                   self.students)


class BaseWriter:
    def writefile(self, filename:str, data: list):
        return NotImplementedError


class JSONFileReader:
    def __init__(self, path: str):
        self.path = path

    def readFile(self):
        return NotImplementedError


class ReadStudents(JSONFileReader):
    def readFile(self) -> list:
        students = []
        with open(self.path, 'r') as f:
            for stud in json.load(f):
                students.append(Student(stud))
        return students


class ReadRooms(JSONFileReader):
    def readFile(self) -> list:
        rooms = []
        with open(self.path, 'r') as f:
            for room in json.load(f):
                rooms.append(RoomWithStudents(room))
        return rooms


class JsonSelectsWriter(BaseWriter):
    def writefile(self, filename: str, data: list):
        with open(filename+'.json', 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)


class XmlSelectsWriter(BaseWriter):
    def writefile(self, filename: str, data: list):
        roomswithstudents = data
        rooms = ET.Element('rooms')
        for rm in roomswithstudents:
            room = ET.SubElement(rooms, 'room')
            roomname = ET.SubElement(room, 'roomname')
            roomname.text = str(rm.name)

        mydata = ET.ElementTree(rooms)
        ET.dump(mydata)
        mydata.write(filename+'.xml', xml_declaration=True)


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


class Writer:
    def __init__(self):
        self.formats = {'json': JsonSelectsWriter(),
                        'xml': XmlSelectsWriter()}

    def choose_format(self, outputformat):
        if outputformat in self.formats:
            return self.formats.get(outputformat)
        else:
            raise ValueError


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

    def execute_queries(self, outputformat):
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


def main():

    parser = argparse.ArgumentParser(description='list merger')
    parser.add_argument('configpath', type=str, help='Enter path to config.ini:')
    parser.add_argument('studentspath', type=str, help='Enter path to students.json:')
    parser.add_argument('roomspath', type=str, help='Enter path to rooms.json:')
    parser.add_argument('outputformat', type=str, choices=['json', 'xml'],
                        help='Choose output method:\n1. JSON\n2.XML')
    args = parser.parse_args()
    config = args.configpath
    students = ReadStudents(args.studentspath).readFile()
    rooms = ReadRooms(args.roomspath).readFile()
    conn = DbWorker(config)
    with conn:
        indexer = IndexWorker(conn.conn)
        conn.insert_rooms(rooms)
        conn.insert_students(students)
        indexer.birth_index()
        indexer.room_index()
        conn.execute_queries(args.outputformat)


if __name__ == "__main__":
    main()
