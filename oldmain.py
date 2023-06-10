from cassandra.cluster import Cluster, BatchStatement, SimpleStatement, PreparedStatement, BoundStatement

if __name__ == '__main__':
    clstr=Cluster(['172.17.0.2'])

    session=clstr.connect('company')

    #query1="CREATE TABLE IF NOT EXISTS Restaurants (ID int, name text, " \
     #      "phone int, address text, type text, PRIMARY KEY(ID));"

    #session.execute(query1)

    #query2 = "INSERT INTO Restaurants (ID, name, phone, address, type) " \
     #        "values (2, 'PizzaHut', 12345, 'Wall st.', 'pizza');
    #session.execute(query2)

    batch=BatchStatement()
    restaurantList=[(4, 'KFC', 543, '11th ST', 'fast food'),
                    (5, 'tokyo sushi', 667, '', 'sushi')]

    for restaurant in restaurantList:
        batch.add(SimpleStatement("INSERT INTO Restaurants (ID, name, phone, address, type)"
                                  "Values (%s,%s,%s,%s,%s)"),
                  (restaurant[0], restaurant[1], restaurant[2], restaurant[3], restaurant[4]))

    session.execute(batch)

    rows = session.execute("select * from restaurants;")

    for row in rows:
        print(row)

    prep = session.prepare("select * from restaurants where ID=?")
    wantedRestaurantIDs = [1, 3]
    for id in wantedRestaurantIDs:
        r = session.execute(prep.bind(id))
        print(r)
