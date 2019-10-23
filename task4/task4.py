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


class SolutionHandler:
    def __init__(self):
        self.rooms_with_students = []

    def listsunion(self, rooms: list, students: list):
        rooms = rooms.copy()
        roomsdict = {}
        for room in rooms:
            roomsdict[room.number] = room
        for stud in students:
            if roomsdict.get(stud.room):
                roomsdict[stud.room].students.append(stud)
            else:
                print('No such room')
        return rooms

    def writefile(self, outputformat: str, rooms):
        if outputformat == 'json':
            JsonWriter().write(rooms=rooms)
        elif outputformat == 'xml':
            XmlWriter().write(rooms=rooms)


class BaseWriter:
    def write(self, rooms: list):
        return NotImplementedError


class JsonWriter(BaseWriter):
    def write(self, rooms: list):
        with open('output.json', 'w') as f:
            json.dump(rooms, f, cls=RoomWithStudentsEncoder, sort_keys=True, indent=4)


class XmlWriter(BaseWriter):
    def write(self, rooms: list):
        roomswithstudents = rooms
        rooms = ET.Element('rooms')
        for rm in roomswithstudents:
            room = ET.SubElement(rooms, 'room')
            roomid = ET.SubElement(room, 'roomid')
            roomname = ET.SubElement(room, 'roomname')
            roomnumber = ET.SubElement(room, 'roomnumber')
            roomstudents = ET.SubElement(room, 'roomstudents')
            roomid.text = str(rm.id)
            roomname.text = str(rm.name)
            roomnumber.text = str(rm.number)
            roomstudents.text = str(rm.students)

        mydata = ET.ElementTree(rooms)
        ET.dump(mydata)
        mydata.write('output.xml', xml_declaration=True)


class RoomWithStudentsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, RoomWithStudents):
            return o.__dict__
        if isinstance(o, Student):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


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


class JsonSelectsWriter:
    def writefile(self, filename: str, data: list):
        with open(filename, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)


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

    def get_all_students(self):
        query = 'SELECT r.*, s.* FROM rooms r, students s WHERE r.RoomNumber = s.StudentRoomNumber ;'
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        rooms_w_students = []
        rooms_dict = {}
        for row in records:
            if not rooms_dict.get(row[2]):
                rooms_dict[row[2]] = RoomWithStudents({'id': row[0], 'name': row[1]})
            rooms_dict[row[4]].students.append(Student(
                    {'id': row[3], 'room': row[4], 'name': row[5], 'birthday': str(row[6]), 'sex': row[7]}))

        return list(rooms_dict.values())

    def get_students_count(self):
        query = """
                SELECT r.RoomName, COUNT(students.StudentID)
                AS total FROM rooms r 
                LEFT JOIN students ON r.RoomNumber = students.StudentRoomNumber 
                GROUP BY r.RoomName
                """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        result = []
        for row in records:
            result.append({'RoomName': row[0], 'StudentsCount': row[1]})
        return result

    def get_top5_avg_age(self):
        query = """
                SELECT rooms.RoomName, from_unixtime(avg(unix_timestamp(students.StudentBirthday)))
                AS total FROM rooms
                LEFT JOIN students ON rooms.RoomNumber=students.StudentRoomNumber GROUP BY rooms.RoomName
                ORDER BY -AVG(students.StudentBirthday) limit 6
                """

        self.cursor.execute(query)
        records = self.cursor.fetchall()
        result = []
        records = records[1:]
        for row in records:
            result.append({'RoomName': row[0], 'Average age': (datetime.datetime.today() - row[1]).days/365.25})
        return result

    def get_top5_max_diff_in_age(self):
        query = """
                SELECT rooms.RoomName, 
                DATEDIFF(MAX(students.StudentBirthday), 
                MIN(students.StudentBirthday)) AS total 
                FROM rooms LEFT JOIN students ON rooms.RoomNumber=students.StudentRoomNumber 
                GROUP BY rooms.RoomName 
                ORDER BY DATEDIFF(MIN(students.StudentBirthday),
                MAX(students.StudentBirthday)) LIMIT 6;
                """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        result = []
        records = records[1:]
        for row in records:
            result.append({'RoomName': row[0], 'Diff in age': row[1]/365.25})
        return result

    def get_rooms_with_diff_sex(self):
        query = """
                SELECT rooms.RoomName AS total FROM rooms 
                JOIN students ON rooms.RoomNumber=students.StudentRoomNumber  
                GROUP BY rooms.RoomName
                HAVING COUNT(DISTINCT students.StudentSEX)>1;
                """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        result = []
        records = records[1:]
        for row in records:
            result.append({'RoomName': row[0]})
        return result

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
    writer = JsonSelectsWriter()
    solution = SolutionHandler()
    with conn:
        indexer = IndexWorker(conn.conn)
        conn.insert_rooms(rooms)
        conn.insert_students(students)
        indexer.birth_index()
        indexer.room_index()
        writer.writefile('stud_count.json', conn.get_students_count())
        solution.writefile(args.outputformat, conn.get_all_students())
        writer.writefile('top5_avg_age.json', conn.get_top5_avg_age())
        writer.writefile('top5_max_age_diff.json', conn.get_top5_max_diff_in_age())
        writer.writefile('rooms_with_diff_sex.json', conn.get_rooms_with_diff_sex())


if __name__ == "__main__":
    main()
