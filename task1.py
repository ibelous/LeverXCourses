import json


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
        return json.JSONEncoder.default(self, o)


def main():
    students, rooms = [], []
    with open('students.json', 'r') as sfile:
        for stud in json.load(sfile):
            students.append(Student(stud))
    with open('rooms.json', 'r') as rfile:
        for room in json.load(rfile):
            rooms.append(RoomWithStudents(room))

    solution = SolutionHandler()
    solution.solution(rooms, students)
    print(rooms[0].students[0].__str__())
    for room in rooms:
        print(room)
    #with open('output.json', 'w') as f:
     #   json.dump(rooms, f, cls=RoomWithStudentsEncoder)


if __name__ == "__main__":
    main()
