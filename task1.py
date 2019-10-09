from collections import defaultdict


def solution(students, rooms):
    rws = defaultdict(list)
    for room in rooms:
        rws[room.get('name')[6:]].append(' ')
    for stud in students:
        rws[str(stud.get('room'))].append(stud.get('name'))
    return rws


def main():
    students = [
        {
            'id': 1,
            'name': 'Nikita #1',
            'room': 1
        },
        {
            'id': 2,
            'name': 'Nikita #2',
            'room': 1
        },
        {
            'id': 3,
            'name': 'Nikita #3',
            'room': 2
        },
        {
            'id': 4,
            'name': 'Nikita #4',
            'room': 2
        },
        {
            'id': 5,
            'name': 'Nikita #5',
            'room': 2
        },
        {
            'id': 6,
            'name': 'Nikita #6',
            'room': 2
        },
        {
            'id': 7,
            'name': 'Nikita #7',
            'room': 3
        }
    ]

    rooms = [
        {
            'id': 1,
            'name': 'Room #1',
            'students': []
        },
        {
            'id': 2,
            'name': 'Room #2',
            'students': []
        },
        {
            'id': 42,
            'name': 'Room #3',
            'students': []
        }
    ]

    rooms_w_students = solution(students, rooms)
    print('result=%s', rooms_w_students)


if __name__ == "__main__":
    main()
