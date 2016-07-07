import sys
import time
import inspect

from vivo_bot import VIVOBot

"""This is a command line interface for VIVOBot to allow people wishing to
avoid writing Python code to run small 'task' files in cronjobs or for
simple report generation.
"""


def run(vb, task_list_file):
    """Open task file and run commands listed"""
    with open(task_list_file, 'r') as f:
        for n, task in enumerate(f):
            if task.endswith('\n'):
                task = task[:-1]
            cmd, args = process_args(task)
            result = process_command(vb, cmd, args)
            log_result(result, n)


def process_args(task):
    """Extract command from line and parse arguments"""
    task_parts = task.split(' ')
    cmd = task_parts[0]
    args = []
    if len(task_parts) > 1:
        args = split_args(task_parts[1:])
    return cmd, args


def split_args(task_parts):
    """Split arguments on spaces and check for strings wrapped in quotes"""
    quoteflag = False
    args = []
    for n, part in enumerate(task_parts):
        if part.startswith('\"') and not quoteflag:
            quoteflag = True
            start = n
        if part.endswith('\"') and quoteflag:
            quoteflag = False
            val = ' '.join(task_parts[start:n+1])
            val = val[1:-1]
            args.append(val)
        elif not quoteflag:
            args.append(part)

    if quoteflag:
        print "ERROR: improperly formatted arguments."
        args = []
    return args


def process_command(vb, cmd, args):
    """Retrieve command from VIVOBot Object and execute it"""
    command = getattr(vb, cmd)
    if not command:
        print "ERROR: Unreconized Command - %s" % cmd
    arg_list = inspect.getargspec(command)[0]
    return command(*args)


def log_result(result, n):
    """Write response from server to a file"""
    if result:
        t = time.strftime("%d-%m-%YT%H.%M.%S")
        with open("logs/"+t+"_cmd_"+str(n), "w") as f:
            f.write(result)


if __name__ == "__main__":

    if len(sys.argv) == 3:
        vb = VIVOBot(sys.argv[1])
    elif len(sys.argv) > 3:
        vb = VIVOBot(sys.argv[1], sys.argv[3])
    else:
        print "Usage: python vb_cli.py [config_file] [task_list] [debug_level]"
        sys.exit(1)

    run(vb, sys.argv[2])
