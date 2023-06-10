from Structures import CassandraClient, Reservation


# TODO stress tests
# write methods for performing stress tests provided in requirements - 5 tests

# TODO update readme, provide schemas


def main():
    # connection [WIP]
    nodes = ['172.17.0.2', '172.17.0.3']
    cassandra_client = CassandraClient(nodes)

    cassandra_client.setup()

    current_reservation_id = 1

    is_working = True
    print("Welcome in the reservation system for SquashDB. What would you like to do?")
    print("1. Make a reservation")
    print("2. Update a reservation")
    print("3. Check a reservation status")
    print("4. Cancel a reservation")
    print("5. Exit the app")
    choice = input("Enter your choice: ")
    while(is_working):
        # MAKING A RESERVATION
        if choice == '1':
            user_id = int(input("Enter your user ID: "))
            equipment = input("Enter the equipment you would like to reserve: ")
            start_time = input("Enter the start time of your reservation: ")
            end_time = input("Enter the end time of your reservation: ")
            reservation = Reservation(current_reservation_id, user_id, 0, equipment, start_time, end_time)
            cassandra_client.create_reservation(reservation)
            print(f"Reservation created with ID: {current_reservation_id}")
            current_reservation_id += 1

        # UPDATING A RESERVATION
        elif choice == '2':
            reservation_id = int(input("Enter the reservation ID: "))
            equipment = input("Enter the new equipment you would like to reserve: ")
            new_start = input("Enter the new start time: ")
            new_end = input("Enter the new end time: ")
            reservation = cassandra_client.get_reservation(reservation_id)
            if reservation:
                reservation.equipment = equipment
                if new_start == reservation.start_time and new_end == reservation.end_time:
                    cassandra_client.equipment_update_reservation(reservation)
                else:
                    reservation.start_time = new_start
                    reservation.new_end = new_end
                    cassandra_client.update_reservation(reservation)
                print(f"Reservation with ID {reservation_id} updated")
            else:
                print(f"No reservation found with ID {reservation_id}")

        # CHECKING A STATUS
        elif choice == '3':
            reservation_id = int(input("Enter the reservation ID: "))
            reservation = cassandra_client.get_reservation(reservation_id)
            if reservation:
                print(f"Reservation with ID {reservation_id} details:")
                print(f"User ID: {reservation.user_id}")
                print(f"Equipment: {reservation.equipment}")
                print(f"Court ID: {reservation.court_id}")
                print(f"Start time: {reservation.start_time}")
                print(f"End time: {reservation.end_time}")
            else:
                print(f"No reservation found with ID {reservation_id}")

        # CANCEL A RESERVATION
        elif choice == '4':
            reservation_id = int(input("Enter the reservation ID: "))
            cassandra_client.cancel_reservation(reservation_id)
            print(f"Reservation with ID {reservation_id} canceled")

        # EXIT
        elif choice == '5':
            print("Thank you for using our reservation system.")
            is_working = False

        # WRONG INPUT
        else:
            choice = input("Enter your choice (1 to 5): ")

        print("Would you like to do anything else?")
        print("1. Make a reservation")
        print("2. Update a reservation")
        print("3. Check a reservation status")
        print("4. Cancel a reservation")
        print("5. Exit the app")
        choice = input("Enter your choice: ")


if __name__ == '__main__':
    main()