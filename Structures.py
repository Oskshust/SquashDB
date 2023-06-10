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
        self.session = cluster.connect('squash')

    def setup(self):
        create_reservations = "CREATE TABLE IF NOT EXISTS reservations (reservation_id int, user_id int, court_id int, " \
                       "equipment text, start_time text, end_time text, PRIMARY KEY (reservation_id));"
        self.session.execute(create_reservations)

        create_courts = "CREATE TABLE IF NOT EXISTS courts (court_id int, was_cleaned int, PRIMARY KEY(court_id));"
        self.session.execute(create_courts)

        # reservation_by_start_time = "CREATE MATERIALIZED VIEW reservations_by_time AS SELECT * FROM reservations " \
        #    "WHERE id IS NOT NULL AND time IS NOT NULL PRIMARY KEY (time)"
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

    def create_reservation(self, reservation):
        # check if there is free court for this hour
        occupied_courts = "SELECT * FROM reservations WHERE start_time = %s;"
        rows = self.session.execute(occupied_courts, reservation.start_time)
        occ = [row.court_id for row in rows]

        all_courts_q = "SELECT * FROM courts;"
        rows = self.session.execute(all_courts_q)
        all_courts = [row.court_id for row in rows]

        if len(occ) == len(all_courts):
            print("There is no court left for this hour, try different one, or try again later.")

        else:
            court_to_be_reserved = list(set(all_courts).difference(occ))[0]
            query = "INSERT INTO reservations (reservation_id, user_id, court_id, equipment, start_time, end_time) VALUES" \
                    "(%s, %s, %s, %s, %s, %s)"
            self.session.execute(query, (reservation.reservation_id, reservation.user_id, court_to_be_reserved, reservation.equipment, reservation.start_time, reservation.end_time))

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
            return Reservation(row.reservation_id, row.user_id, row.court_id, row.equipment, row.start_time, row.end_time)

    def cancel_reservation(self, reservation_id):
        query = "DELETE FROM reservations WHERE reservation_id = %s"
        self.session.execute(query, (reservation_id,))
