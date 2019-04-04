"""
4D Geolocation Use Case EnTK Analysis Script
==========================================================
This script contains the EnTK Pipeline script for the 4DGeolocation
(ASIFT) Usecase.

Author: Aymen Alsaadi
Email : aymen.alsaadi@rutgers.edu
License: MIT
Copyright: 2018-2019
"""
from __future__ import print_function
import os
import argparse
import random
import json
from radical.entk import Pipeline, Stage, Task, AppManager


def args_parser():

    '''
    Argument Parsing Function for the script.
    '''
    parser = argparse.ArgumentParser(description='Executes the 4DGeolocation pipeline')
    parser.add_argument('name', type=str,
                        help='name of the execution. It has to be a unique value')
    parser.add_argument('src_img', type=str,
                        help='Source Image Path ')
    parser.add_argument('dataset', type=str,
                        help='data_set path for target images')
    parser.add_argument('desc', type=int,
                        help='Matching Method SIFT=1, SURF=2, Root-SIFT=11 (Default)')
    parser.add_argument('resources', type=str,
                        help='HPC resource on which the script will run.')
    parser.add_argument('project', type=str,
                        help='The project that will be charged')
    parser.add_argument('queue', type=str,
                        help='The queue from which resources are requested.')
    parser.add_argument('walltime', type=int,
                        help='The amount of time resources are requested in' + ' minutes')
    parser.add_argument('cpus', type=int,
                        help='Number of CPU Cores required to execute')
    print (parser.parse_args())
    return parser.parse_args()


def generate_discover_pipeline(path, src_img):

    '''
    This function takes a single source image and path of set of images as an input on a specific
    resource and returns a JSON file for all the images that exist in that path as an arguments.
    '''
    # Create a dicoverer Pipeline object
    pipeline = Pipeline()
    pipeline.name = 'Parser'

    # Create a Stage object
    stage = Stage()
    stage.name = 'Parser-S0'
    task = Task()
    task.name = 'Parser-T0'
    task.pre_exec = ['module load psc_path/1.1',
                     'module load slurm/default',
                     'module load intel/18.4',
                     'module load xdusage/2.1-1',
                     'module load python2/2.7.11_gcc_np1.11',
                     'module load gcc/5.3.0',
                     'module load opencv/2.4.13.2']
    task.executable = 'python2'
    # Assign arguments for the task executable
    task.arguments = ['../img_parser.py', '%s' % path, '%s' % src_img]
    task.download_output_data = ['images.json']
    stage.add_tasks(task)
    # Add Stage to the Pipeline
    pipeline.add_stages(stage)

    return pipeline


def generate_pipeline(img1, img2, x1, y1, x2, y2, name):

    """
    This function will generate number of pipleines based on
    the number of images being dicovered by the parser_pipleine.
    """
    args = args_parser()

    # Create a Pipeline object
    p = Pipeline()
    p.name = name
    source_img = img1
    target_img = img2

    # Create a "KeyPoints_Generation" Stage object
    s1 = Stage()
    s1.name = 'KeyPoints Generation'

    # Create a Task object
    t1 = Task()
    t1.name = 'Task1'
    t1.pre_exec = ['module load psc_path/1.1',
                   'module load slurm/default',
                   'module load intel/18.4',
                   'module load xdusage/2.1-1',
                   'module load python2/2.7.11_gcc_np1.11',
                   'module load gcc/5.3.0',
                   'module load opencv/2.4.13.2']
    # Assign executable to the task
    t1.executable = '../ASIFT/src/phase_2_keypoint_generation/fast_imas_IPOL/build/main'

    # Assign arguments for the task executable
    t1.arguments = ['-im1_gdal', source_img, 1000, 1000, x1, y1,
                    '-im2_gdal', target_img, 1000, 1000, x2, y2,
                    '-desc', args.desc]

    t1.cpu_reqs = {'processes': 1,
                   'threads_per_process': 1,
                   'thread_type': None}

    # Add the Task to the Stage
    s1.add_tasks(t1)

    # Add Stage to the Pipeline
    p.add_stages(s1)

    # Create a "RANSAC" Stage object
    s2 = Stage()
    s2.name = 'RANSAC Filter'

    # Create a Task object
    t1 = Task()
    t1.name = 'Task1'
    t1.pre_exec = ['module load psc_path/1.1',
                   'module load slurm/default',
                   'module load intel/18.4',
                   'module load xdusage/2.1-1',
                   'module load python2/2.7.11_gcc_np1.11',
                   'module load gcc/5.3.0',
                   'module load opencv/2.4.13.2']
    t1.executable = 'python2'
    t1.link_input_data = ['$Pipeline_%s_Stage_%s_Task_%s/data_matches.csv'%(p.name, s1.name, t1.name)]

    # Assign arguments for the task executable
    t1.arguments = ['../ASIFT/src/phase_3_ransac_filtering/ransac_filter.py',
                    '-img1_filename', source_img,
                    '-img1_nodata', 0,
                    '-img2_filename', target_img,
                    '-img2_nodata', 0,
                    'data_matches.csv', 'ransac.csv']
    t1.cpu_reqs = {'processes': 1,
                   'threads_per_process': 1,
                   'thread_type': None}

    # Download the Ransaced keypoints file
    t1.download_output_data = ['ransac.csv']
    s2.add_tasks(t1)
    p.add_stages(s2)

    return p


if __name__ == '__main__':

    args = args_parser()
    hostname = os.environ.get('RMQ_HOSTNAME', 'localhost')
    port = os.environ.get('RMQ_PORT', 33235)
    res_dict = {'resource': args.resources,
                'walltime': args.walltime,
                'cpus': args.cpus,
                'project': args.project,
                'queue': args.queue,
                'schema': 'gsissh'}

    # Assign resource manager to the Application Manager
    appman = AppManager(hostname=hostname, port=port, name='entk.session-%s-%s'
                        % (args.name, random.randint(9999, 100000)),
                        autoterminate=False, write_workflow=True)
    # Assign resource request description to the Application Manager
    appman.resource_desc = res_dict
    parser_pipeline = generate_discover_pipeline(args.dataset, args.src_img)
    appman.workflow = set([parser_pipeline])

    # Run the Application Manager for the parser_pipeline
    appman.run()
    jsonfile = open("images.json", "r")
    jsonObj = json.load(jsonfile)
    counter = 0
    pipelines = list()
    # Generate pipelines based on the number of the images found in the target dataset
    for item in range(0, len(jsonObj["Dataset"])):
        img1 = jsonObj['Dataset'][0]['img1']
        img2 = jsonObj['Dataset'][counter]['img2']
        x1 = jsonObj['Dataset'][0]['x1']
        x2 = jsonObj['Dataset'][0]['x2']
        y1 = jsonObj['Dataset'][counter]['y1']
        y2 = jsonObj['Dataset'][counter]['y2']
        counter = counter+1
        p1 = generate_pipeline(img1, img2, x1, y1, x2, y2, name='Pipeline%s' % item)
        pipelines.append(p1)

    # Assign the workflow as a set or list of Pipelines to the Application Manager
    # Note: The list order is not guaranteed to be preserved
    appman.workflow = set(pipelines)
    # Run the Application Manager for the main pipeline
    appman.run()
    print('Done')
    # Now that all images have been performed the matching
    # and filtering process
    # release the resources.
    appman.resource_terminate()
