from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import requests
from kafka import KafkaProducer
import logging
import time
default_args={
    'owner':'airscholar',
    'start_date':datetime(2024,10,6,12,00)
    
}

def get_data():
    response=requests.get('https://randomuser.me/api/')
    if response.status_code==200:
        data=response.json()
        results=data['results'][0]
        return results

def format_data(res):
    if res is None:
        raise ValueError("Input data is None. Ensure valid data is passed.")
    
    # Initialize an empty dictionary
    data = {}
    
    # Extract and format fields from 'res', making sure 'res' contains valid values
    try:
        data['first_name'] = res['name']['first']
        data['last_name'] = res['name']['last']
        data['gender'] = res['gender']
        data['address'] = f"{str(res['location']['street']['number'])} {res['location']['street']['name']}, {res['location']['city']}, {res['location']['state']}, {res['location']['country']}"
        data['postcode'] = res['location']['postcode']
        data['email'] = res['email']
        data['username'] = res['login']['username']  # 'username' is under 'login'
        data['dob'] = res['dob']['date']
        data['registered_date'] = res['registered']['date']
        data['phone'] = res['phone']
        data['picture'] = res['picture']['medium']
    
    except KeyError as e:
        raise KeyError(f"Missing expected key in response: {e}")
    
    return data

    
    

def stream_data():
   
    print(json.dumps(res,indent=3))
    producer=KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    current_time=time.time()
    while True:
        if time.time()>current_time+60:
            break
        try:
            res=get_data()
            res=format_data(res)
            producer.send('users_created',json.dumps(res).encode('utf-8'))
            producer.flush()
        except Exception as e:
            logging.error(f'An error occured: {e}')
   
    
   

with DAG('user_automation', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    
    streaming_task=PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )
    
    
stream_data() 