from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager
import os
##import logger
# ------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'DEBUG'
    os.environ['RADICAL_PILOT_VERBOSE'] ='DEBUG'


if __name__ == '__main__':

    # Create a Pipeline object
    p = Pipeline()

    # Create a Stage object
    s = Stage()

    # Create a Task object
    t = Task()
    t.name = 'task1'        # Assign a name to the task (optional)
    t.executable =['/demo_ASIFT']
    t.arguments=['adam1.png','adam2.png','imgOutVert.png','imageOutHori.png','matchings.txt','keypoints0.txt','keypoints2.txt']
    t.upload_input_data= ['adam1.png', 'adam2.png', 'imgOutVert.png', 'imgOutHori.png', 'matchings.txt', 'keypoints1.txt', 'keypoints2.txt']  # Assign arguments for the task executable


    # Add Task to the Stage
    s.add_tasks(t)

    # Add Stage to the Pipeline
    p.add_stages(s)


    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

            'resource': 'xsede.comet',
            'walltime': 10,
            'cores': 1,
            'project': '',
            'queue':'debug',
            'schema': 'gsissh'
    }

    # Create Resource Manager object with the above resource description
    rman = ResourceManager(res_dict)

    # Create Application Manager
    appman = AppManager(port=32769)

    # Assign resource manager to the Application Manager
    appman.resource_manager = rman

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.assign_workflow(set([p]))

    # Run the Application Manager
    appman.run()

