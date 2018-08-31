from radical.entk import Pipeline, Stage, Task, AppManager
import os
import argparse

# ------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

os.environ['RADICAL_ENTK_PROFILE'] = 'True'

if not os.environ.get('RADICAL_PILOT_DBURL'):
    os.environ['RADICAL_PILOT_DBURL'] = "mongodb://MONGO_DB_URL/radicallab"

def generate_pipeline(name, stages):
  
    #Condition function "Simply check if data_matches.csv file is exist and not empty"
    def func_condition():

        my_path = "/home/usr/ASIFT/PHASE_1_KEYPOINT_GENERATION/fast_imas_IPOL/build/data_matches.csv"
        if os.path.exists(my_path) and os.path.getsize(my_path) > 0:
            return True
           
        return False

    #True Condition function
    def func_on_true():

        s2 = Stage() # Create a Stage object
        t = Task()    
        t.executable = ['/bin/echo']   
        t.cpu_reqs['process_type'] = ''
        t.cpu_reqs['thread_type'] = ''
        t.arguments = ["This is Adaptive Stage on True"] 
        t.cores = 20
        s2.add_tasks(t)  # Add the Task to the Stage
        p.add_stages(s2) 

    #False Condition function
    def func_on_false():
   
        s1=Stage() # Create a Stage object
        t1 = Task()    
        t1.executable = ['/bin/echo']   
        t1.cpu_reqs['process_type'] = ''
        t1.cpu_reqs['thread_type'] = ''
        t1.arguments = ["This is Adaptive Stage on False"] 
        t1.cores = 20
        s1.add_tasks(t1) # Add the Task to the Stage
        p.add_stages(s1)     

    # Create a Pipeline object
    p = Pipeline()
    p.name = name

    # Create a Stage object
    s = Stage()
    s.name = 'Stage1'

    # Create a Task object
    t = Task()
    t.name = 'task1'        # Assign a name to the task (optional)
    t.executable ='/home/usr/SummerRadical/ASIFT/PHASE_1_KEYPOINT_GENERATION/fast_imas_IPOL/build/main'   # Assign executable to the task
    t.cpu_reqs['process_type'] = ''
    t.cpu_reqs['thread_type'] = ''
    t.arguments = ['-im1','input_0.png','-im2' ,'input_1.png','-desc',11,'-covering' ,1.4]# Assign arguments
    t.upload_input_data= ['input_0.png', 'input_1.png','covering.png']
    t.download_output_data = ['data_matches.csv']

    # Add post-exec to the Stage
    s.post_exec = {
                             'condition': func_condition,
                             'on_true'  : func_on_true,
                             'on_false' : func_on_false
                    }

    # Add the Task to the Stage
    s.add_tasks(t)
    # Add Stage to the Pipeline
    p.add_stages(s)
    # Create a Stage object
    s3 = Stage()
    s3.name = 'Stage3'
  
    # Create a Task object
    t3 = Task()
    t3.name = 'task3'              # Assign a name to the task (optional)
    t3.executable =['/bin/bash']   # Assign executable to the task
    t3.cpu_reqs['process_type'] = ''
    t3.cpu_reqs['thread_type'] = ''
    t3.arguments = ['-l', '-c', 'base64 /dev/urandom | head -c 1000000 > output.txt'] # Assign arguments
    t3.upload_input_data= []

    # Add the Task to the Stage
    s3.add_tasks(t3)
    # Add Stage to the Pipeline
    p.add_stages(s3)

    return p 


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Scaling inputs')
    parser.add_argument('cores', type=int, help='Number of Cores')
    parser.add_argument('pipelines',type=int ,help='Number of pipelines')
    print parser.parse_args()
    args = parser.parse_args()

    res_dict = {
                  'resource': 'xsede.comet_anaconda',
                  'walltime': 10,
                  'cpus'   : args.cores,
                  'project' : '',
                  'queue'   : 'compute',
                  'schema'  :'gsissh',

               } 

    # Create Application Manager
    appman = AppManager(port=32769,hostname='localhost')
 
    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict

    pipelines = list()
    for cnt in range(args.pipelines):
        p1 = generate_pipeline(name ='Pipeline%s'%cnt,stages = 1)
        pipelines.append(p1)
        
    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow=set(pipelines)

    # Run the Application Manager
    appman.run()
