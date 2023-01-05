## Obviously, my config file is called config_nogit.py, but here's what it should look like.

## to use prepare for the network stack:
##  --> set the slug, vpc vpc_id, private subnets, and private subnet ciders.
##  --> leave everything else alone unless you know what you're changing.



config = {
         'slug' : 'HelloAwsAuroraServerless',
         'user' : 'afraser',
         'account': '76457*******',
         'region' : 'us-east-1',
         'network' : {
            'vpc-name': 'CfVpcConstruct',
            'vpc_id' : 'vpc-****', 
            'private_subnet_ids' : ['subnet-******','subnet-******'],
            'sn1_cider': '10.0.2.0/24',
            'sn2_cider' : '10.0.3.0/24',
            'availability_zones' : ['us-east-1a']
         },
         'db': {
            'default_database_name' : 'postgres'
         },
         'ecs' :{
            'family': 'HelloAwsAuroraServerlessDev',
            'image' : '76457*******.dkr.ecr.us-east-1.amazonaws.com/fargate-hello-world:latest',
            'command': ["python", "./app.py", "hello", "world"]
         },
         'lambda' : {
            'comment': 'theses are layer versions already installed',
            'numpy_version' : 'numpy-1-22-1-python38-x86-64:3',
            'pandas_version' : 'pandas-1-3-5-python38-x86-64:3',
            'psycopg2_version' : 'psycopg2-2-9-3-python38-x86-64:1'

         }
}
         
