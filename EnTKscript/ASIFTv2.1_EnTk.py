from radical.entk import Pipeline, Stage, Task, AppManager
import os
import argparse

# Set default verbosity

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

os.environ['RADICAL_ENTK_PROFILE'] = 'True'

if not os.environ.get('RADICAL_PILOT_DBURL'):
    os.environ['RADICAL_PILOT_DBURL'] = "mongodb://LINK_FOR THE _MONGODB"

def generate_pipeline(name, stages):

    #condition function
    def func_condition():

        print 'Condition Function Started'
        my_path = "~/data_matches.csv"

        
        if os.path.exists(my_path) and os.path.getsize(my_path) > 0:
            return True


        return False

    #True Condition function
    def func_on_true():
        print 'True Function'

        s2 = Stage()
        t = Task()
        t.pre_exec = ['module load python2']
        t.executable = ['/bin/echo']
        t.cpu_reqs['process_type'] = ''
        t.cpu_reqs['thread_type'] = ''
        t.arguments = ["This is Adaptive Stage on True"]
        t.cores = 20
        # Add the Task to the Stage
        s2.add_tasks(t)

        # Add post-exec to the Stage

        p.add_stages(s2)

    #False Condition function
    def func_on_false():
        print 'False Function'

        s1=Stage()


        # Create a Stage object

        t1 = Task()
        t1.pre_exec = ['module load python2']
        t1.executable = ['/bin/echo']
        t1.arguments = ["This is Adaptive Stage on False"]
        t1.cores = 20

        # Add the Task to the Stage
        s1.add_tasks(t1)

        # Add post-exec to the stage
        # Add Stage to the Pipeline
        p.add_stages(s1)



    # Create a Pipeline object
    p = Pipeline()
    p.name = name

    # Create a Stage object
    s = Stage()
    print 'ASIFT STAGE Begins'
    s.name = 'Stage1'
    # Create a Task object
    t = Task()
    t.name = 'task1'        # Assign a name to the task (optional)
    t.pre_exec = ['module load python2']
    t.executable ='~/ASIFTv2.1/ASIFT/PHASE_1_KEYPOINT_GENERATION/fast_imas_IPOL/build/main'   # Assign executable to the task
    t.arguments = ['-im1_gdal','/TIF_img/10MB.tif',5000,1000,2000,2000,'-im2_gdal','/TIF_img/10MB.tif',5000,1000,2000,2000]# Assign arguments
    t.upload_input_data= ['/TIF_img/10MB.tif', '/TIF_img/10MB.tif']
    t.download_output_data = ['data_matches.csv']
    s.post_exec = {
                             'condition': func_condition,
                             'on_true': func_on_true,
                             'on_false': func_on_false
                    }

    # Add the Task to the Stage
    s.add_tasks(t)

    # Add Stage to the Pipeline
    p.add_stages(s)


    # Create a Stage object
    s3 = Stage()
    s3.name = 'Stage3'
    print 'Third SRAGE Begins'
    # Create a Task object
    t3 = Task()
    t3.pre_exec = ['module load python2']
    t3.name = 'task3'        # Assign a name to the task (optional)
    t3.executable =['/bin/bash']   # Assign executable to the task
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
    parser.add_argument('queue',type=str, help='Queue to submit to')
    parser.add_argument('pipelines',type=int ,help='Number of pipelines')
    print parser.parse_args()
    args = parser.parse_args()



    res_dict = {
                  'resource' : '',
                  'walltime': 10,
                  'cpus'   : args.cores,
                  'project' : '',
                  'queue'   : '',
                  'queue'   :'',
                  'schema'  :'gsissh',

               }

    # Create Application Manager
    appman = AppManager(port= ****,hostname='****')

    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict
    pipelines = list()
    for cnt in range(args.pipelines):
        p1 = generate_pipeline(name ='Pipeline%s'%cnt,stages = 3)
        #dev = dev ^ 1
        pipelines.append(p1)

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow=set(pipelines)

    # Run the Application Manager
    appman.run()
