import os
import json
from tapipy import actors, util, errors
from tapipy.tapis import Tapis
from pathlib import Path
import dataclasses
from typing import Any

JOB = Path("/opt/job.json")
UPLOAD_DIR = '/work2/05369/urrutia/frontera/uploads'

def main() -> None:
    context = actors.get_context()  # type: ignore
    #print(json.dumps(context, indent=4))

    # And we'll read in our job definition json to use for submitting a job
    with open(JOB, "r") as f:
        job = json.load(f)

    # For people who don't have docker, you can optionally define path/appid in a message to the actor
    upload_dir = context.message_dict.get('upload_dir')
    if upload_dir is None:
        upload_dir=os.path.normpath(UPLOAD_DIR)
    else:
        upload_dir = os.path.normpath(upload_dir)
    appid = context.message_dict.get('appId')
    if appid is not None:
        job['appId'] = appid

    # First we need to get our tapis client so we can interact with systems and submit jobs
    t = actors.get_client()
    # there is a bug in the base url, this is a simple patch to remove the trailing slash
    t.base_url = t.base_url.strip('/')
    # Lets check our upload directory to see all the files that have been uploaded
    files = t.files.listFiles(systemId='frontera', path=upload_dir)
    # files.listFiles returns tapipy files objects, we just need a list of paths
    # so we can use list comprehension to create a list of file paths
    input_files = [file.path for file in files]

    # We'll use a "submitted.txt" file to keep track of inputs that have been submitted
    # the first time you run this that file won't exist, so we'll wrap this step in a try/except
    # so we can create that submitted list the first time the actor runs
    try:
        # Try reading in the contents of submitted.txt
        submitted_file = t.files.getContents(systemId='frontera',path=upload_dir+'/submitted.txt')
        # files.getContents returns a bytes object of the file contents, 
        # so we decode it and turn it into a list
        submitted = [sub.decode() for sub in submitted_file.splitlines()]
    except errors.NotFoundError as e:
        # for our first run, we'll add "submitted.txt", so that new file doesn't trigger another job submission
        submitted = [upload_dir.strip('/')+'/submitted.txt']

    # Another example of list comprehension to create a list of files that are 
    # in the upload directory, but not in the "submitted.txt" file
    unsubmitted = [path for path in input_files if path not in submitted]
    # For any input that hasn't been submitted, lets create a new job
    for path in unsubmitted:
        print(path)
        # sets the input for the job
        job['parameterSet']['appArgs'][0]['arg'] = '/'+path
        # set the archive location for the job
        job['archiveSystemDir'] = upload_dir.replace('uploads','products')
        # submits the job
        resp = t.jobs.submitJob(**job)
        # print the job uuid so we'll have it in the logs
        print("Submitted Job: {}".format(resp.uuid))
        # add the input to our "submitted" list
        submitted.append(path)

    # If this actor doesn't submit any jobs, we don't need to update "submitted.txt"
    # and we can just close out
    if unsubmitted == [] and len(submitted) > 1:
        print("No new uploads detected")
        exit()
    # Save a local version of submitted.txt
    with open(r'submitted.local', 'w') as fp:
        for item in submitted:
            # write each item on a new line
            fp.write("%s\n" % item)
    # Upload our local, updated version of submitted.txt to the upload dir so we don't resubmit the same job
    t.upload(source_file_path="submitted.local", system_id="frontera", dest_file_path=upload_dir+"/submitted.txt")
    print("updated submitted.txt")



if __name__ == "__main__":
    main()
