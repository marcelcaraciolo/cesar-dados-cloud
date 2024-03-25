import sys
from os import path
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType



LANDING_BUCKET = 'landing-5gflix-211125401641'
TRANSFORMING_BUCKET = "transformed-5gflix-211125401641"

args = getResolvedOptions(sys.argv,
                          ['JOB_NAME'])

sc = SparkContext()
glue_context = GlueContext(sc)
# Init my job
job = Job(glue_context)
job.init(args['JOB_NAME'], args)

print('Accessing S3 bucket...')
# Let's use Amazon S3

spark = glue_context.spark_session

movies = spark.read\
    .format("csv")\
    .option("header", "false")\
    .option("delimiter", ";")\
    .option("inferSchema", "true")\
    .load("s3://" + LANDING_BUCKET + '/' + 'movies.csv')
movies = movies.toDF('movie_id', 'movie')
movies = movies.withColumn('movie', F.regexp_replace('movie', '[\\(\\)]', ''))
movies = movies.withColumn('movie_year_split', F.split(movies['movie'], ','))\
                          .select('movie_id', 'movie',F.element_at(F.col('movie_year_split'), -1).alias('year')
                                 )
movies = movies.withColumn("year", movies["year"].cast(IntegerType()))
movies = movies.dropna()
movies.show()
movies.printSchema()

ratings = spark.read\
    .format("csv")\
    .option("header", "true")\
    .option("delimiter", ";")\
    .option("inferSchema", "true")\
    .load("s3://" + LANDING_BUCKET + '/' + 'customers_rating.csv')
ratings = ratings.toDF('cust_id', 'rating', 'date', 'movie_id')
ratings = ratings.withColumn('date', F.to_date('date'))
ratings = ratings.dropna()
ratings.show()
ratings.printSchema()

destination_movies_path = path.join("s3://", TRANSFORMING_BUCKET, "movies")
destination_ratings_path = path.join("s3://", TRANSFORMING_BUCKET, "ratings")


movies.write.format("parquet")\
    .mode("overwrite")\
    .save(destination_movies_path)


ratings.write.format("parquet")\
    .mode("overwrite")\
    .save(destination_ratings_path)

job.commit()


