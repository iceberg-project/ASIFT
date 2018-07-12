#ASIFTv2 EnTK Script (PHASE 1)



from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager
import os

# ------------------------------------------------------------------------------
# Set default verbosity
if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'


def generate_pipeline(name, stages):

    # Create a Pipeline object
    p = Pipeline()
    p.name = 'pipe'

    # Create a Stage object
    s = Stage()
    s.name = 'Stage0'

    # Create a Task object
    t = Task()
    t.name = 'task0'        # Assign a name to the task (optional)
    t.executable ='/main'   # Assign executable to the task
    t.arguments = ['-im1','input_0.png','-im2' ,'input_1.png','-desc',11,'-covering' ,1.4]# Assign arguments
    t.upload_input_data= ['input_0.png', 'input_1.png','covering.png']

    # Add Task to the Stage
    s.add_tasks(t)
    # Add Stage to the Pipeline
    p.add_stages(s)

    #create new Stage object
    s1=Stage()
    s1.name='Stage1'

    # Create a Task object
    t1 = Task()
    t1.name = 'task0'        # Assign a name to the task (optional)
    t1.executable ='/bin/echo'   # Assign executable to the task
    t1.arguments = ['Hello World']# Assign arguments
     # Add Task to the Stage
    s1.add_tasks(t1)
    # Add Stage to the Pipeline
    p.add_stages(s1)



    return p



if __name__ == '__main__':

    p1 = generate_pipeline(name='Pipeline 1', stages=2)
    p2 = generate_pipeline(name='Pipeline 2', stages=2)
    p3 = generate_pipeline(name='Pipeline 3', stages=2)
    p4 = generate_pipeline(name='Pipeline 4', stages=2)
    p5 = generate_pipeline(name='Pipeline 5', stages=2)



    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

            'resource': 'xsede.comet_anaconda',
            'walltime': 10,
            'cores': 1,
            'project': '',
            'queue'  : 'debug',
            'schema' : 'gsissh',
    }

    # Create Resource Manager object with the above resource description
    rman = ResourceManager(res_dict)

    # Create Application Manager
    appman = AppManager(port=32769)
     # Assign resource manager to the Application Manager
    appman.resource_manager = rman

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.assign_workflow(set([p1, p2, p3, p4, p5])) 

    # Run the Application Manager
    appman.run()
