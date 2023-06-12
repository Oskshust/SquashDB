# Squash DB

* Oskar Szudzik 148245,
* Krystian Moras 148243

## Description

The project is supposed to be a reservation system for squash courts. 

The client is able to reserve a court, update the reservation, see its status/descritpion and cancel it. 

We provided a GUI for the convenience of making a process easier and running tests more intuitive.

Each reservation consists of its id, id of court, user id, start and end times of reservation, equipment (client can comment here what would does he/she need e.g. a pair of rackets or a ball). 

In the next section we provide a schemas for reservation table as well as for courts table.  

Court is chosen for client as a first not-occupied court at the start_time of reservation.

## Schemas
We created 2 tables with schemas as below

```
reservations (reservation_id int, 
                user_id text, 
                court_id int, 
                equipment text, 
                start_time text, 
                end_time text, 
                PRIMARY KEY (reservation_id));
```
```
courts (court_id int, 
        was_cleaned int, 
        PRIMARY KEY(court_id));
```
We also used a following index:
```
reservations_by_time ON reservations (start_time);
```

## Problems

We used TIMESTAMP as a way of solving issues with a lot of reservations being done at the same time.

## How to run

1. Use commands from command.txt to create cassandra nodes and keyspace.
2. Install required libraries.
3. run  ```python3 app.py```