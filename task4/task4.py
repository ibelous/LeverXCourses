import argparse
import DBworker
import IOobjects
import objects


def main():

    parser = argparse.ArgumentParser(description='list merger')
    parser.add_argument('configpath', type=str, help='Enter path to config.ini:')
    parser.add_argument('studentspath', type=str, help='Enter path to students.json:')
    parser.add_argument('roomspath', type=str, help='Enter path to rooms.json:')
    parser.add_argument('outputformat', type=str, choices=['json', 'xml'],
                        help='Choose output method:\n1. JSON\n2.XML')
    args = parser.parse_args()
    config = args.configpath
    students = IOobjects.ReadStudents(args.studentspath).readFile(objects.Student)
    rooms = IOobjects.ReadRooms(args.roomspath).readFile(objects.RoomWithStudents)
    conn = DBworker.DbWorker(config)
    with conn:
        indexer = DBworker.IndexWorker(conn.conn)
        conn.insert_rooms(rooms)
        conn.insert_students(students)
        indexer.birth_index()
        indexer.room_index()
        conn.execute_queries(args.outputformat, IOobjects.Writer)


if __name__ == "__main__":
    main()
