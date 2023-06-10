from cassandra.cluster import Cluster


class Reservation:
    def __init__(self, reservation_id, user_id, court_id, equipment, start_time, end_time):
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.court_id = court_id
        self.equipment = equipment
        self.start_time = start_time
        self.end_time = end_time


class Equipment:
    def __init__(self, number_of_balls, number_of_rockets):
        self.number_of_balls = number_of_balls
        self.number_of_rockets = number_of_rockets


class CassandraClient:
    def __init__(self, nodes):
        cluster = Cluster(nodes, port=9042)
        #create_keyspace = "CREATE KEYSPACE IF NOT EXISTS squash WITH REPLICATION={\'class\': \'SimpleStrategy\', \'replication_factor\': 1};"
        self.session = cluster.connect('squash')

    def setup(self):
        create_reservations = "CREATE TABLE IF NOT EXISTS reservations (reservation_id int, user_id int, court_id int, " \
                       "equipment text, start_time text, end_time text, PRIMARY KEY (reservation_id));"
        self.session.execute(create_reservations)

        create_courts = "CREATE TABLE IF NOT EXISTS courts (court_id int, was_cleaned int, PRIMARY KEY(court_id));"
        self.session.execute(create_courts)

        insert_courts = "INSERT INTO courts (court_id, was_cleaned) VALUES (%s, %s);"
        self.session.execute(insert_courts, (1, 1))
        self.session.execute(insert_courts, (2, 1))
        self.session.execute(insert_courts, (3, 0))

        self.sanity_check()

    def sanity_check(self):
        sanity_check = "SELECT * FROM courts"
        rows = self.session.execute(sanity_check)
        for row in rows:
            print(row)

    def create_reservation(self, reservation):
        query = "INSERT INTO reservations (reservation_id, user_id, equipment, start_time, end_time) VALUES (%s, %s, %s, %s, %s)"
        self.session.execute(query, (reservation.reservation_id, reservation.user_id, reservation.equipment, reservation.start_time, reservation.end_time))

    def update_reservation(self, reservation):
        query = "UPDATE reservations SET equipment = %s WHERE reservation_id = %s"
        self.session.execute(query, (reservation.equipment, reservation.reservation_id))

    def get_reservation(self, reservation_id):
        query = "SELECT * FROM reservations WHERE reservation_id = %s"
        rows = self.session.execute(query, (reservation_id,))
        for row in rows:
            return Reservation(row.reservation_id, row.user_id, row.equipment, row.start_time, row.end_time)

    def cancel_reservation(self, reservation_id):
        query = "DELETE FROM reservations WHERE reservation_id = %s"
        self.session.execute(query, (reservation_id,))