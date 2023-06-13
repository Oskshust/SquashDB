# dash app

import dash

from dash import dcc, html, Input, Output, State, DiskcacheManager

from Structures import CassandraClient, Reservation
from cassandra.protocol import SyntaxException


import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

app = dash.Dash(__name__,background_callback_manager=background_callback_manager)


nodes = ['172.17.0.2', '172.17.0.3']
cassandra_client = CassandraClient(nodes)

cassandra_client.setup()

current_reservation_id = cassandra_client.get_reservation_id()
if not current_reservation_id:
    current_reservation_id=0

app.layout = html.Div([
    dcc.Store(id="thread_key",data=None),
    dcc.Interval(
            id='interval-component',
            interval=1*100, # in milliseconds
            n_intervals=0
        ),
    # FORM WITH USER NAME, EQUIPMENT, START TIME AND END TIME
    html.Div([
        html.Div([
            html.Label('User Name'),
            dcc.Input(id='input-name', type='text', value=''),
            html.Label('Equipment'),
            # CHOICES FOR SQUAH EQUIPMENT
            dcc.Dropdown(
                id='input-equipment',
                options=[
                    {'label': 'Racket', 'value': 'Racket'},
                    {'label': 'Ball', 'value': 'Ball'},
                    {'label': 'Goggles', 'value': 'Goggles'}
                ],
                value='Racket'
            ),
            html.Label("Court"),
            dcc.Dropdown(
                id="input-court",
                options=[
                    {'label': "Court 1", "value":1},
                    {'label': "Court 2", "value":2},
                    {'label': "Court 3", "value":3},
                ],
                value=1
            ),
            html.Label('Start Time'),
            # tIME PICKER
            dcc.Input(id='input-start', type='text', value=''),
            html.Label('End Time'),
            dcc.Input(id='input-end', type='text', value=''),
            html.Label("Reservation id"),
            dcc.Input(id="input-id", type='number', value=current_reservation_id),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            
            html.Div(id='output-state')
        ],
        # display flex rows
        style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '33%'}),
    # find reservation
    html.Div([
        html.Label('Cancel Reservation'),
        dcc.Input(id='input-cancel', type='number', value=current_reservation_id),
        html.Button(id='cancel-button', n_clicks=0, children='Cancel reservation'),
        html.Div(id='output-cancel'),
        html.Div(id="output-cancel2")
    ], style={'display': 'flex', 'flex-direction': 'column', 'width': '30%'}),
    # show courts schedule
    html.Div([
        html.Div([
            html.Label('Court 1'),
            html.Div(id='court1')
        ],
        style={'display': 'flex', 'flex-direction': 'column', 'width': '33%'}),
        html.Div([
            html.Label('Court 2'),
            html.Div(id='court2')
        ],
        style={'display': 'flex', 'flex-direction': 'column', 'width': '33%'}),
        html.Div([
            html.Label('Court 3'),
            html.Div(id='court3')
        ],
        style={'display': 'flex', 'flex-direction': 'column', 'width': '33%'})
    ],
    # display flex columns
    style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
    # stress test 5 buttons
    html.Div([
        html.Button(id='stress-button1', n_clicks=0, children='Large data test'),
        html.Button(id='stress-button2', n_clicks=0, children='Client same request test'),
        #dcc.Checklist(id='stress-button3',options=["Start random actions"], value=[]),
        html.Button(id='stress-button3', n_clicks=0, children='Start random requests'),
        html.Button(id='cancel_button3', n_clicks=0, children='Stop random requests',disabled=True),
        
        html.Button(id='stress-button4', n_clicks=0, children='Immeadiate occupancy'),
        html.Button(id='stress-button5', n_clicks=0, children='Constant reservation and cancellations'),
        html.Button(id='reset-all',children="Reset all"),
        html.Div(id='stress-output1'),
        html.Div(id='stress-output2'),
        html.Div(id='stress-output3'),
        html.Div(id='stress-output4'),
        html.Div(id='stress-output5')
    ],
    # display flex columns
    style={'display': 'flex', 'flex-direction': 'column', 'width': '20%'}),
],
# display flex columns
style={'display': 'flex', 'flex-direction': 'row'}
)


# CALLBACK TO PRINT THE FORM VALUES
@app.callback(Output('output-state', 'children'),
              Output('input-id','value'),
                [Input('submit-button', 'n_clicks')],
                [State('input-name', 'value'),
                State('input-equipment', 'value'),
                State('input-start', 'value'),
                State('input-end', 'value'),
                State('input-id','value'),
                State('input-court',"value")],
                prevent_initial_call=True)
def add_reservation(n_clicks, name, equipment, start, end, id, court):
    global current_reservation_id
    reservation = Reservation(id, name, court, equipment, start, end)
    try:
        result = cassandra_client.create_reservation(reservation)
    except SyntaxException:
        return "Invalid input", current_reservation_id

    if result == []:
        current_reservation_id= cassandra_client.get_reservation_id() +1
    return result, current_reservation_id

@app.callback(Output('output-cancel2', 'children',allow_duplicate=True),
                Input('reset-all', 'n_clicks'),
                prevent_initial_call=True)
def cancel_all(n_clicks):

    result = cassandra_client.cancel_all()
    return "Cancelled all"

# CALLBACK TO PRINT THE FIND RESERVATION VALUE
@app.callback(Output('output-cancel', 'children',allow_duplicate=True),
                Input('cancel-button', 'n_clicks'),
                State('input-cancel', 'value'),
                prevent_initial_call=True)
def cancel_reservation(n_clicks, id):

    result = cassandra_client.cancel_reservation(id)
    if result == []:
        return f"Successfully canceled reservation {id}"
    
    else:
        return "Weird error"


from timeit import default_timer as timer
# CALLBACK TO PRINT THE STRESS BUTTON VALUES
@app.callback(Output('stress-output1', 'children'),
                [Input('stress-button1', 'n_clicks')],
                prevent_initial_call=True)
def update_output1(n_clicks):
    global current_reservation_id
    start = timer()
    for i in range(1000):
            reservation = Reservation(current_reservation_id,"Test",i%3+1,"Racket",str(i//3),str((i//3)+1))
            cassandra_client.create_reservation(reservation)
            current_reservation_id+=1
    end = timer()
    return f"Finished load stress test in {end-start}"

@app.callback(Output('stress-output2', 'children'),
                [Input('stress-button2', 'n_clicks')],
                prevent_initial_call=True)
def update_output2(n_clicks):
    start = timer()
    reservation = Reservation(1,"CLIENT",1,"RACKET","0","1")
    for i in range(1000):
        cassandra_client.update_reservation(reservation)
    end = timer()
    return f"Finished client makes the same request test in {end-start}"

import time
import random


import threading
thread_map = dict()

def random_action(user_number, condition):
    while not condition.is_set():     
        reservation = Reservation(random.randint(0,9)+(user_number*100),f"User{user_number}",random.randint(1,3),"Racket","1","2")

        result = cassandra_client.create_reservation(reservation)

        cassandra_client.cancel_reservation(random.randint(0,9)+(user_number*100))

@app.callback(
    Output("stress-output3", "children", allow_duplicate=True),
    Output("stress-button3","disabled", allow_duplicate=True),
    Output("cancel_button3","disabled", allow_duplicate=True),
    Output("thread_key","data", allow_duplicate=True),
    Input("stress-button3", "n_clicks"),
    State("thread_key","data"),
    prevent_initial_call=True
)
def start_random(n_clicks, thread_key):
    if thread_key is None: 
        user_number = random.randint(0,10)
        condition = threading.Event()
        threading.Thread(target=random_action, args=(user_number,condition)).start()
        thread_map[user_number] = condition
    
        return "Started random requests", True, False, user_number
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("stress-output3", "children", allow_duplicate=True),
    Output("stress-button3","disabled", allow_duplicate=True),
    Output("cancel_button3","disabled", allow_duplicate=True),
    Output("thread_key","data", allow_duplicate=True),
    Input("cancel_button3", "n_clicks"),
    State("thread_key","data"),
    prevent_initial_call=True
)
def stop_random(n_clicks, thread_key):
    print(thread_key)
    if thread_key is not None:
        
        thread_map[thread_key].set()
        print(thread_map)
        del thread_map[thread_key]

        return "Stopped random requests", False, True, None
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update




@app.callback(Output('stress-output4', 'children'),
                [Input('stress-button4', 'n_clicks')],
                prevent_initial_call=True)  
def update_output4(n_clicks):

    def occupy_all(user_id):
        reservation = Reservation(reservation_id=user_id*1000+1,
                                  user_id=f"User{user_id}",
                                  court_id=1,
                                  equipment="Racket",
                                  start_time="0",
                                  end_time="1")
        cassandra_client.create_reservation(reservation)
        reservation.reservation_id+=1
        reservation.court_id = 2
        cassandra_client.create_reservation(reservation)
        reservation.reservation_id+=2
        reservation.court_id = 3
        cassandra_client.create_reservation(reservation)

    thread1 = threading.Thread(target=occupy_all,args=(1,),daemon=True)
    thread2 = threading.Thread(target=occupy_all,args=(2,), daemon=True)
    thread1.start()
    thread2.start()
        
        


    return 
import time

@app.callback(Output('stress-output5', 'children'),
                [Input('stress-button5', 'n_clicks')],
                prevent_initial_call=True)
def update_output5(n_clicks):
    def constant_reservations_and_cancellations():
        for i in range(50):
            reservation = Reservation(4242,"Undecided",1,"Racket","42","43")
            result = cassandra_client.create_reservation(reservation)
            time.sleep(0.2)
            print(result)
            cassandra_client.cancel_reservation(4242)
            time.sleep(0.2)
    thread = threading.Thread(target=constant_reservations_and_cancellations,daemon=True)
    thread.start()
        
    return "Constant reservations for 10 seconds"

# Update courts every interval

@app.callback(Output('court1','children'),Output('court2','children'),Output('court3','children'),
              Input('interval-component', 'n_intervals'))
def update_courts(n_intervals):
    courts = sorted(cassandra_client.get_courts(), key= lambda x: x.start_time)
    reservations_1 = [
        html.Div([str(reservation.reservation_id)+" ",reservation.user_id+" ", reservation.equipment+" ", reservation.start_time+" ", reservation.end_time+" "]) for reservation in courts if reservation.court_id==1]
    reservations_2 = [
        html.Div([str(reservation.reservation_id)+" ",reservation.user_id+" ", reservation.equipment+" ", reservation.start_time+" ", reservation.end_time+" "]) for reservation in courts if reservation.court_id==2]
    reservations_3 = [
        html.Div([str(reservation.reservation_id)+" ",reservation.user_id+" ", reservation.equipment+" ", reservation.start_time+" ", reservation.end_time+" "]) for reservation in courts if reservation.court_id==3]
    
    return reservations_1, reservations_2, reservations_3


if __name__ == '__main__':
    app.run_server(debug=False)
