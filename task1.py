import json
import xml.etree.ElementTree as ET


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
    print('Enter path to students.json(Default: ./students.json):')
    studentspath = input()
    with open(studentspath or 'students.json', 'r') as sfile:
        for stud in json.load(sfile):
            students.append(Student(stud))
    print('Enter path to rooms.json(Default: ./rooms.json):')
    roomspath = input()
    with open(roomspath or 'rooms.json', 'r') as rfile:
        for room in json.load(rfile):
            rooms.append(RoomWithStudents(room))
    roomlist = rooms

    solution = SolutionHandler()
    solution.solution(rooms, students)
    print('Choose output method(default-JSON):\n1. JSON\n2.XML')
    if input() == '2':
        '''rooms = ET.Element('rooms')
        room = ET.SubElement(rooms, 'room')
        roomid = ET.SubElement(room, 'roomid')
        roomname = ET.SubElement(room, 'roomname')
        roomnumber = ET.SubElement(room, 'roomnumber')
        roomstudents = ET.SubElement(room, 'roomstudents')
        studentid = ET.SubElement(roomstudents, 'studentid')
        studentname = ET.SubElement(roomstudents, 'studentname')
        rooms.set('rooms', roomlist)
        mydata = ET.XML(ET.tostring(rooms))
        print(mydata)
        with open('output.xml', 'w') as f:
            f.write(str(ET.tostring(mydata)))'''
        pass
    else:
        with open('output.json', 'w') as f:
            json.dump(rooms, f, cls=RoomWithStudentsEncoder, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
