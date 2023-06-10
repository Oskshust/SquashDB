from Structures import CassandraClient, Reservation

# TODO setting up the cassandra nodes
# it might be just script in readme or dockerfile or any suitable form really


# setting up nodes:
# docker run --name cas1 -p 9042:9042 -e CASSANDRA_CLUSTER_NAME=MyCluster -d cassandra
# check IP and set proper one in 'nodes' var
# docker inspect --format='{{.NetworkSettings.IPAddress}}' cas1
# docker exeec -it CONTAINER_NAME cqlsh
# "CREATE KEYSPACE IF NOT EXISTS squash WITH REPLICATION={'class': 'SimpleStrategy', 'replication_factor': 1};"
# (below) not checked yet
# docker run --name cas2 -e CASSANDRA_SEEDS="$(docker inspect --format='{{.NetworkSettings.IPAddress}}' cas1)" -e CASSANDRA_CLUSTER_NAME=MyCluster -d cassandra

# TODO making a reservation
# users decides at which hour he needs a court. Then the reservation runs proper query to check which courts
# are already taken - query should be probably joined with query on courts to suggest one which is free.

# TODO error handling
# Write some while loops for user not to crush app with wrong input or updating/canceling reservation which is not there

# TODO stress tests
# write methods for performing stress tests provided in requirements - 5 tests

# TODO update readme, provide schemas


def main():
    # connection [WIP]
    nodes = ['172.17.0.2']
    cassandra_client = CassandraClient(nodes)

    cassandra_client.setup()

    current_reservation_id = 1

    is_working = True
    print("What would you like to do?")
    print("1. Make a reservation")
    print("2. Update a reservation")
    print("3. Check a reservation status")
    print("4. Cancel a reservation")
    print("5. Exit the app")
    choice = input("Enter your choice: ")
    while(is_working):
        # MAKING A RESERVATION
        if choice == '1':
            user_id = input("Enter your user ID: ")
            equipment = input("Enter the equipment you would like to reserve: ")
            start_time = input("Enter the start time of your reservation: ")
            end_time = input("Enter the end time of your reservation: ")
            reservation = Reservation(current_reservation_id, user_id, equipment, start_time, end_time)
            cassandra_client.create_reservation(reservation)
            print(f"Reservation created with ID: {current_reservation_id}")
            current_reservation_id += 1

        # UPDATING A RESERVATION
        elif choice == '2':
            reservation_id = input("Enter the reservation ID: ")
            equipment = input("Enter the new equipment you would like to reserve: ")
            reservation = cassandra_client.get_reservation(reservation_id)
            if reservation:
                reservation.equipment = equipment
                cassandra_client.update_reservation(reservation)
                print(f"Reservation with ID {reservation_id} updated")
            else:
                print(f"No reservation found with ID {reservation_id}")

        # CHECKING A STATUS
        elif choice == '3':
            reservation_id = input("Enter the reservation ID: ")
            reservation = cassandra_client.get_reservation(reservation_id)
            if reservation:
                print(f"Reservation with ID {reservation_id} details:")
                print(f"User ID: {reservation.user_id}")
                print(f"Equipment: {reservation.equipment}")
                print(f"Start time: {reservation.start_time}")
                print(f"End time: {reservation.end_time}")
            else:
                print(f"No reservation found with ID {reservation_id}")

        # CANCEL A RESERVATION
        elif choice == '4':
            reservation_id = input("Enter the reservation ID: ")
            cassandra_client.cancel_reservation(reservation_id)
            print(f"Reservation with ID {reservation_id} canceled")

        # EXIT
        elif choice == '5':
            print("Thank you for using our reservation system.")
            is_working = False

        # WRONG INPUT
        else:
            choice = input("Enter your choice (1 to 4)")


if __name__ == '__main__':
    main()