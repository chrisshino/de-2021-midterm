import airflow
from airflow import DAG
import io
import csv
from datetime import datetime, timedelta
import boto3
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.operators.s3_to_redshift_operator import S3ToRedshiftTransfer

DEFAULT_ARGS =  {
  'owner': 'wcd_data_engineer',
  'depends_on_past': False,
  'start_date': airflow.utils.dates.days_ago(0),
  'email': ['chris.shino@hotmail.com'],
  'email_on_failure': False,
  'email_on_retry': False
}

CLUSTER_ID = "j-3PU5IHBGZSX0Q"

SPARK_STEPS = [
  {
    'Name':'wcd_data_engineer_bootcamp2',
    'ActionOnFailure': "CONTINUE",
    'HadoopJarStep': {
      'Jar': 'command-runner.jar',
      'Args': [
        '/usr/bin/spark-submit',
        '--master', 'yarn',
        '--deploy-mode', 'cluster',
        '--num-executors', '2',
        '--driver-memory', '512m',
        '--executor-memory', '3g',
        '--executor-cores', '2',
        '--py-files','s3://data-engineering-midterm-cs/job.zip',
        's3://data-engineering-midterm-cs/workflow_entry.py',
        '-p', "{'input_path': '{{ task_instance.xcom_pull('parse_request', key='s3location') }}', 'name': 'class_demo', 'file_type': 'csv', 'output_path': 's3://test-bucket-1997/fighter_data'}"
      ]
    }
  }

]

def retrieve_s3_files(**kwargs):
  s3_location = kwargs['dag_run'].conf['s3_location']
  kwargs['ti'].xcom_push(key="s3location", value = s3_location)

def find_and_rename_file():
  s3 = boto3.resource('s3')
  s3Client = boto3.client('s3')
  my_bucket = s3.Bucket("test-bucket-1997")
  obj_list = []
  for object in my_bucket.objects.filter(Prefix="fighter_data/"):
    print(object.key)
    obj_list.append(object.key)
  s3_object = s3Client.get_object(Bucket='test-bucket-1997', Key=obj_list[1])
  writer_buffer = io.StringIO()
  data = s3_object['Body'].read().decode('utf-8')
  writer = csv.writer(writer_buffer)
  split = data.split('\n')[1:]
  joined = '\n'.join(split)
  reader = csv.reader(io.StringIO(joined), delimiter=",")
  writer.writerows(reader)
  
  buffer_to_upload = io.BytesIO(writer_buffer.getvalue().encode())
  s3Client.put_object(Body = buffer_to_upload, Bucket="test-bucket-1997", Key="fighter_output/fighters.csv")
  # s3.Object('test-bucket-1997',f'fighter_output/fighters.csv').copy_from(CopySource=f"test-bucket-1997/{obj_list[1]}")
  

dag = DAG(
  'emr_job_flow_manual_steps_dag',
  default_args = DEFAULT_ARGS,
  dagrun_timeout = timedelta(hours=2),
  schedule_interval=None
)

parse_request = PythonOperator(
  task_id = "parse_request",
  provide_context=True,
  python_callable=retrieve_s3_files,
  dag=dag
)

step_adder = EmrAddStepsOperator(
  task_id = 'add_steps',
  job_flow_id = CLUSTER_ID,
  aws_conn_id = "aws_default",
  steps = SPARK_STEPS, 
  dag = dag
)

step_checker = EmrStepSensor(
  task_id = 'watch_step',
  job_flow_id = CLUSTER_ID,
  step_id = "{{ task_instance.xcom_pull('add_steps', key='return_value')[0]}}",
  aws_conn_id = "aws_default",
  dag=dag
)

find_rename_s3 = PythonOperator(
  task_id = "find_rename_s3",
  python_callable= find_and_rename_file,
  dag=dag
)

task_transfer_s3_to_redshift = S3ToRedshiftTransfer(
    s3_bucket="test-bucket-1997",
    redshift_conn_id="redshift",
    aws_conn_id="my_s3",
    s3_key="fighter_output",
    schema="ufc",
    table="fighters",
    copy_options=['csv'],
    task_id='transfer_s3_to_redshift',
    dag=dag
)



step_adder.set_upstream(parse_request)
step_checker.set_upstream(step_adder)
find_rename_s3.set_upstream(step_checker)
task_transfer_s3_to_redshift.set_upstream(find_rename_s3)