import json
import xml.etree.ElementTree as ET
import argparse


class Student:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.name = data.get('name')
        self.room = data.get('room')

    def __str__(self):
        return 'id: {}, name: {}, room: {}'.format(self.id, self.name, self.room)

    def __repr__(self):
        return 'id: {}, name: {}, room: {}'.format(self.id, self.name, self.room)


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

    def solution(self, rooms: list, students: list):
        roomsdict = {}
        for room in rooms:
            roomsdict[room.number] = room
        for stud in students:
            if roomsdict.get(stud.room):
                roomsdict[stud.room].students.append(stud)
            else:
                print('No such room')


class RoomWithStudentsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, RoomWithStudents):
            return o.__dict__
        if isinstance(o, Student):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def main():
    students, rooms = [], []
    parser = argparse.ArgumentParser(description='list merger')
    parser.add_argument('studentspath', type=str, help='Enter path to students.json(Default: ./students.json):')
    parser.add_argument('roomspath', type=str, help='Enter path to rooms.json(Default: ./rooms.json):')
    parser.add_argument('jsonXML', type=str, help='Choose output method(default-JSON):\n1. JSON\n2.XML')
    args = parser.parse_args()
    with open(args.studentspath or 'students.json', 'r') as sfile:
        for stud in json.load(sfile):
            students.append(Student(stud))
    with open(args.roomspath or 'rooms.json', 'r') as rfile:
        for room in json.load(rfile):
            rooms.append(RoomWithStudents(room))
    roomlist = rooms

    solution = SolutionHandler()
    solution.solution(rooms, students)
    if args.jsonXML == '2':
        rooms = ET.Element('rooms')
        room = ET.SubElement(rooms, 'room')
        roomid = ET.SubElement(room, 'roomid')
        roomname = ET.SubElement(room, 'roomname')
        roomnumber = ET.SubElement(room, 'roomnumber')
        roomstudents = ET.SubElement(room, 'roomstudents')
        studentid = ET.SubElement(roomstudents, 'studentid')
        studentname = ET.SubElement(roomstudents, 'studentname')
        mydata = ET.ElementTree(rooms)
        print(mydata)
        with open('output.xml', 'w') as f:
            mydata.write(f)
            #f.write(str(ET.tostring(mydata)))
        pass
    else:
        with open('output.json', 'w') as f:
            json.dump(rooms, f, cls=RoomWithStudentsEncoder, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
