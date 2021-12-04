import argparse
import ast
from pipeline_workflow.default_workflow import DefaultWorkflow
from pipeline_utils.package import SparkParams 
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--params", required=True, help="Spark input parameters")
args = parser.parse_args()

print('args ' + str(args))

def parse_command_line(args):
    """Convert a command line argument to a dict
    """
    return ast.literal_eval(args)


def spark_init(parser_name):
    """
    To initiallize sparkSession 
    """
    ss = SparkSession \
        .builder \
        .appName(parser_name) \
        .getOrCreate()
    ss.sparkContext.setLogLevel("ERROR")
    return ss

params = parse_command_line(args.params)
print('running stuff ' + str(params))
params = SparkParams(params)
spark = spark_init(params.args['name'])

if __name__ == "__main__":
    '''
    checking if the script is being run via command 'python script'
 
    '''
    print("Executing script via python")
    #spark.read.parquet('file:/data/wcd').show()
    dataflow = DefaultWorkflow(params, spark)
    #spark.sparkContext.getConf().getAll()
    dataflow.run()
else:
    print("Importing script")