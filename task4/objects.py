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
