from cassandra.cluster import Cluster
from datetime import datetime

TIME_BOUNDARY = 2000000000

class Reservation:
    def __init__(self, reservation_id, user_id, court_id, equipment, start_time, end_time):
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.court_id = court_id
        self.equipment = equipment
        self.start_time = start_time
        self.end_time = end_time


class CassandraClient:
    def __init__(self, nodes):
        cluster = Cluster(nodes, port=9042)
        self.session = cluster.connect('squash')

    def setup(self):
        create_reservations = "CREATE TABLE IF NOT EXISTS reservations (reservation_id int, user_id text, court_id int, " \
                              "equipment text, start_time text, end_time text, PRIMARY KEY (reservation_id));"
        self.session.execute(create_reservations)

        create_courts = "CREATE TABLE IF NOT EXISTS courts (court_id int, was_cleaned int, PRIMARY KEY(court_id));"
        self.session.execute(create_courts)

        reservation_by_start_time = "CREATE INDEX IF NOT EXISTS reservations_by_time ON reservations (start_time);"
        self.session.execute(reservation_by_start_time)

        insert_courts = "INSERT INTO courts (court_id, was_cleaned) VALUES (%s, %s);"
        self.session.execute(insert_courts, (1, 1))
        self.session.execute(insert_courts, (2, 1))
        self.session.execute(insert_courts, (3, 0))

        # self.sanity_check()

    def sanity_check(self):
        sanity_check = "SELECT * FROM courts"
        rows = self.session.execute(sanity_check)
        for row in rows:
            print(row)

    def get_reservation_id(self):
        reservation_id_query = "Select max(reservation_id) from reservations"
        reservation_id = self.session.execute(reservation_id_query)
        reservation_id = reservation_id.all()[0].system_max_reservation_id
        print(reservation_id)
        return reservation_id

    def get_courts(self):
        courts_query = "SELECT * FROM reservations"

        reservations = self.session.execute(courts_query)
        reservations = reservations.all()
        return [Reservation(row.reservation_id, row.user_id, row.court_id, row.equipment, row.start_time, row.end_time)
                for row in reservations]

    def create_reservation(self, reservation):
        # check if there is free court for this hour
        occupied_court_query = f"SELECT * FROM reservations WHERE start_time = '{reservation.start_time}';"
        results = self.session.execute(occupied_court_query)
        for row in results.all():
            if reservation.court_id == row.court_id:
                return "This court is already occupied"

        query = "INSERT INTO reservations (reservation_id, user_id, court_id, equipment, start_time, end_time) VALUES" \
                "(%s, %s, %s, %s, %s, %s) USING TIMESTAMP %s"
        result = self.session.execute(query, (
            reservation.reservation_id, reservation.user_id, reservation.court_id, reservation.equipment,
            reservation.start_time, reservation.end_time, TIME_BOUNDARY - int(round(datetime.now().timestamp()))))
        result = result.all()
        return result

    def equipment_update_reservation(self, reservation):
        query = "UPDATE reservations SET equipment = %s WHERE reservation_id = %s"
        self.session.execute(query, (reservation.equipment, reservation.reservation_id))

    def update_reservation(self, reservation):
        self.cancel_reservation(reservation.reservation_id)
        self.create_reservation(reservation)

    def get_reservation(self, reservation_id):
        query = "SELECT * FROM reservations WHERE reservation_id = %s"
        rows = self.session.execute(query, (reservation_id,))
        for row in rows:
            return Reservation(row.reservation_id, row.user_id, row.court_id, row.equipment, row.start_time,
                               row.end_time)

    def cancel_reservation(self, reservation_id):
        query = "DELETE FROM reservations WHERE reservation_id = %s"
        result = self.session.execute(query, (reservation_id,))
        result = result.all()
        return result

    def cancel_all(self):
        drop_table = "Drop table reservations;"
        self.session.execute(drop_table)
        create_reservations = "CREATE TABLE IF NOT EXISTS reservations (reservation_id int, user_id text, court_id int, " \
                              "equipment text, start_time text, end_time text, PRIMARY KEY (reservation_id));"
        self.session.execute(create_reservations)

        reservation_by_start_time = "CREATE INDEX IF NOT EXISTS reservations_by_time ON reservations (start_time);"
        self.session.execute(reservation_by_start_time)
