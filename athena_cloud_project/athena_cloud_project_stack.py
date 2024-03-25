from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_glue as glue,
    aws_iam as iam,
    aws_athena as athena,
    aws_ec2 as ec2,
)

import aws_cdk as cdk
from constructs import Construct


class AthenaCloudProjectStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            scope=self,
            id="VPC",
            vpc_name="my_VPC",
            gateway_endpoints={
                "s3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            },
            nat_gateways=0,
        )

        # creating the buckets where the data files will be placed
        landing_bucket = s3.Bucket(
            self,
            '"5GFlix"-development-landing-bucket',
            bucket_name=f"landing-5gflix-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # creating the buckets where the transformed files will be placed
        transforming_bucket = s3.Bucket(
            self,
            '"5GFlix"-development-transforming-bucket',
            bucket_name=f"transformed-5gflix-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # creating the bucket where the Athena queries output will be placed
        query_output_bucket = s3.Bucket(
            self,
            "5GFlix-development-query-output-bucket",
            bucket_name=f"5gflix-analysis-output-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # S3 Bucket to host glue scripts
        glue_bucket = s3.Bucket(
            self,
            "5GFlix-development-glue-scripts-bucket",
            bucket_name=f"glue-scripts-5gflix-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # uploading the data files to the bucket
        s3_deployment.BucketDeployment(
            self,
            "5GFlix-development-files",
            destination_bucket=landing_bucket,
            sources=[s3_deployment.Source.asset("./resources/data-files")],
            content_type="text/csv",
            retain_on_delete=False,
            memory_limit=1024,
            use_efs=True,
            vpc=vpc,
        )

        # asset to sync local scripts folder with S3 bucket
        asset = s3_deployment.Source.asset("./resources/glue-scripts")

        # Sync local scripts with S3 bucket
        s3_deployment.BucketDeployment(
            self,
            "DeployGlueJobScripts",
            sources=[asset],
            destination_bucket=glue_bucket,
            destination_key_prefix="glue-python-scripts",
        )

        # creating the permissions for the crawler to enrich our Data Catalog and glue transformation job
        glue_role = iam.Role(
            self,
            "glue-crawler-role",
            role_name="glue-crawler-role",
            assumed_by=iam.ServicePrincipal(service="glue.amazonaws.com"),
            managed_policies=[
                # Remember to apply the Least Privilege Principle and provide only the permissions needed to the crawler
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AmazonS3FullAccess",
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                ),
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AWSGlueServiceRole",
                    "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
                ),
            ],
        )

        # Grant read write access for glue execution IAM role for S3 bucket
        glue_bucket.grant_read_write(glue_role)

        # Grant read and write roles for these landing ans transform buckets
        transforming_bucket.grant_read_write(glue_role)
        landing_bucket.grant_read_write(glue_role)

        scriptLocation = (
            "s3://" + glue_bucket.bucket_name + "/glue-python-scripts/transform_job.py"
        )

        # pre-process data files (transformation step - joining using pyspark)
        job = glue.CfnJob(
            self,
            "5GFlix-development-transformation-job",
            name="5GFlix-python-job",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl", python_version="3", script_location=scriptLocation
            ),
            glue_version="3.0",
        )

        # creating the Glue Database to serve as our Data Catalog
        glue_database = glue.CfnDatabase(
            self,
            "5GFlix-development-database",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="5gflix-database"
            ),
        )

        # creating the Glue Crawler that will automatically populate our Data Catalog. Don't forget to run the crawler
        # as soon as the deployment finishes, otherwise our Data Catalog will be empty. Check out the README for more instructions
        glue.CfnCrawler(
            self,
            "5GFlix-development-crawler",
            name="5GFlix-crawler",
            database_name=glue_database.database_input.name,
            role=glue_role.role_name,
            targets={
                "s3Targets": [
                    {"path": f"s3://{transforming_bucket.bucket_name}/movies"},
                    {"path": f"s3://{transforming_bucket.bucket_name}/ratings"},
                ]
            },
        )

        # creating the Athena Workgroup to store our queries
        work_group = athena.CfnWorkGroup(
            self,
            "5GFlix--development-queries-work-group",
            name="5GFlix-analysis",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location=f"s3://{query_output_bucket.bucket_name}",
                    encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                        encryption_option="SSE_S3"
                    ),
                )
            ),
        )
        # pergunta 1.1
        query_11 = athena.CfnNamedQuery(
            self,
            "query-11",
            database=glue_database.database_input.name,
            work_group=work_group.name,
            name="query-11",
            query_string='SELECT count(distinct(movie_id)) FROM "5gflix-database"."movies"',
        )

        # pergunta 1.2
        query_12 = athena.CfnNamedQuery(
            self,
            "query-12",
            database=glue_database.database_input.name,
            work_group=work_group.name,
            name="query-12",
            query_string='SELECT "5gflix-database"."movies".movie, avg(rating) as rating_avg FROM "5gflix-database"."ratings" left join "5gflix-database"."movies" on "5gflix-database"."ratings".movie_id = "5gflix-database"."movies".movie_id group by "5gflix-database"."movies".movie order by avg(rating) desc limit 5',
        )
        
        #pergunta 1.3
        query_13 = athena.CfnNamedQuery(
            self,
            "query-13",
            database=glue_database.database_input.name,
            work_group=work_group.name,
            name="query-13",
            query_string='SELECT year, count(*) as total_launches from "5gflix-database"."movies" group by year order by total_launches asc limit 9',
        )
        
        #pergunta 1.4
        query_14 = athena.CfnNamedQuery(
            self,
            "query-14",
            database=glue_database.database_input.name,
            work_group=work_group.name,
            name="query-14",
            query_string='SELECT "5gflix-database"."ratings".cust_id, count(*) as total_eval  FROM "5gflix-database"."ratings"  group by "5gflix-database"."ratings".cust_id  order by total_eval desc limit 5',
        )
        
        # pergunta 1.5
        query_15 = athena.CfnNamedQuery(
            self,
            "query-15",
            database=glue_database.database_input.name,
            work_group=work_group.name,
            name="query-15",
            query_string='SELECT "5gflix-database"."ratings".cust_id, count(*) as total_eval  FROM "5gflix-database"."ratings"  group by "5gflix-database"."ratings".cust_id  order by total_eval desc limit 5',
        )



        # adjusting the resource creation order
        query_11.add_dependency(work_group)
        query_12.add_dependency(work_group)
        query_13.add_dependency(work_group)
        query_14.add_dependency(work_group)
        query_15.add_dependency(work_group)
