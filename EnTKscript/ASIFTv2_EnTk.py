# ASIFTv2 code
# EntK script 7.3 (PHASE 1)


from radical.entk import Pipeline, Stage, Task, AppManager
import os
import argparse
#------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'


def generate_pipeline(name, stages):

    # Create a Pipeline object
    p = Pipeline()
    p.name = name

    # Create a Stage object
    s = Stage()
    s.name = 'Stage1'

    # Create a Task object
    t = Task()
    t.name = 'task1'        # Assign a name to the task (optional)
    t.executable ='/ASIFT_V2/ASIFT/PHASE_1_KEYPOINT_GENERATION/fast_imas_IPOL/build/main'   # Assign executable to the task
    t.arguments = ['-im1','input_0.png','-im2' ,'input_1.png','-desc',11,'-covering' ,1.4]# Assign arguments
    t.upload_input_data= ['input_0.png', 'input_1.png','covering.png']

    # Add the Task to the Stage
    s.add_tasks(t)

    # Add Stage to the Pipeline
    p.add_stages(s)

    return p

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Scaling inputs')
    parser.add_argument('cores', type=int, help='Number of Cores')
    #parser.add_argument('queue',type=str, help='Queue to submit to')
    parser.add_argument('pipelines',type=int ,help='Number of pipelines')
    print parser.parse_args()
    args = parser.parse_args()



    res_dict = {

                  'resource': 'xsede.comet',
                  'walltime': 10,
                  'cpus'   : args.cores,
                  'project' : '',
                  'queue'   : 'debug',
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
