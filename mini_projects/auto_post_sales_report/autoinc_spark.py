
from pyspark import SparkContext

sc = SparkContext(appName="MakeYearCount")

raw_rdd = sc.textFile("/user/root/spark_mini_project1/input/data.csv")

def extract_vin_key_value(line):
    parts = line.split(",")
    vin = parts[2]
    incident_type = parts[1]
    make = parts[3] if len(parts) > 3 else None
    year = parts[5] if len(parts) > 5 else None
    return (vin, (incident_type, make, year))
    
in_kv = raw_rdd.map(lambda x: extract_vin_key_value(x))


def populate_make(pairRdd):
    vin, auto_info = pairRdd
    make, year = None, None
    
    for info in auto_info:
        if info[0] == 'I':
            make = info[1]
            year = info[2]
    
    updated_pairs = [] 
    
    for info in auto_info:
            new_make = info[1] if info[1] else make
            new_year = info[2] if info[2] else year
            updated_pairs.append((vin, (info[0], new_make, new_year)))
            
    return updated_pairs

enhance_make = in_kv.groupByKey().flatMap(lambda kv: populate_make(kv))

def extract_make_key_value(vehicle_kv):
    make_kv = []
    
    vin , value = vehicle_kv
    make = value[1]
    year = value[2]
    return ((make, year), 1)
    
make_kv = enhance_make.map(lambda x: extract_make_key_value(x))

automobile_post_sales_report = make_kv.reduceByKey(lambda a, b: a + b).map(lambda x: "{}-{},{}".format(x[0][0], x[0][1], x[1]))

automobile_post_sales_report.saveAsTextFile("hdfs:///user/root/spark_mini_project1/output/automobile_post_sales_report")