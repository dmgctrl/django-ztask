Installing
==========

Download and install 0MQ version 2.1.3 or better from http://www.zeromq.org
Install pyzmq and django_ztaskd using PIP:

    pip install pyzmq
    pip install -e git@github.com:dmgctrl/django-ztask.git#egg=django_ztask

Add `django\_ztask` to your `INSTALLED\_APPS` setting in `settings.py`, and run `syncdb`

    python manage.py syncdb
    

Running the server
==================

Run django-ztask using the manage.py command:

    python manage.py ztaskd


Command-line arguments
----------------------

The ztaskd command takes a series of command-line arguments:

- `--noreload`

  By default, `ztaskd` will use the built-in django reloader 
  to reload the server whenever a change is made to a python file. Passing
  in `--noreload` will prevent it from listening for changed files.
  (Good to use in production.)

- `-l` or `--loglevel`

  Choose from the standard `CRITICAL`, `ERROR`, `WARNING`, 
  `INFO`, `DEBUG`, or `NOTSET`. If this argument isn't passed 
  in, `INFO` is used by default.

- `-f` or `--logfile`

  The file to log messages to. By default, all messages are logged
  to `stdout`

- `--replayfailed`

  If a command has failed more times than allowed in the 
  `ZTASKD_RETRY_COUNT` (see below for more), the task is
  logged as failed. Passing in `--replayfailed` will cause all 
  failed tasks to be re-run.


Settings
--------

There are several settings that you can put in your `settings.py` file in 
your Django project. These are the settings and their defaults

    ZTASKD_URL = 'tcp://127.0.0.1:5555'

By default, ztaskd will run over TCP, listening on 127.0.0.1 port 5555. 

    ZTASKD_ALWAYS_EAGER = False

If set to `True`, all `.async` and `.after` tasks will be run in-process and
not sent to the `ztaskd` process. Good for task debugging.

    ZTASKD_DISABLED = False

If set, all tasks will be logged, but not executed. This setting is often 
used during testing runs. If you set `ZTASKD_DISABLED` before running 
`python manage.py test`, tasks will be logged, but not executed.

    ZTASKD_RETRY_COUNT = 5

The number of times a task should be reattempted before it is considered failed.

    ZTASKD_RETRY_AFTER = 5

The number, in seconds, to wait in-between task retries. 


Running in production
---------------------

A recommended way to run in production would be to put something similar to 
the following in to your rc.local file. This example has been tested on 
Ubuntu 10.04 and Ubuntu 10.10:

    #!/bin/bash -e
    pushd /var/www/path/to/site
    sudo -u www-data python manage.py ztaskd --noreload -f /var/log/ztaskd.log &
    popd


Making functions in to tasks
============================

Decorators and function extensions make tasks able to run. 
Unlike some solutions, tasks can be in any file anywhere. 
When the file is imported, `ztaskd` will register the task for running.

The @task Decorator
-------------------

The `@task()` decorator will turn any normal function in to a 
`django_ztask` task if called using one of the function extensions.

Function extensions
-------------------

Any function can be called in one of three ways:

- `func(args, *kwargs)`

  Calling a function normally will bypass the decorator and call the function directly

- `func.async(args, **kwargs)`

  Calling a function with `.async` will cause the function task to be called asyncronously 
  on the ztaskd server. For backwards compatability, `.delay` will do the same thing as `.async`, but is deprecated.

- `func.after(seconds, args, **kwargs)`

  This will cause the task to be sent to the `ztaskd` server, which will wait `seconds` 
  seconds to execute.


Example
-------

    from django_ztask import task
    
    @task()
    def print_this(what_to_print):
        print what_to_print
        
    if __name__ == '__main__':
        
        # Call the function directly
        print_this('Hello world!')
        
        # Call the function asynchronously
        print_this.async('This will print to the ztaskd log')
        
        # Call the function asynchronously
        # after a 5 second delay
        print_this.after(5, 'This will print to the ztaskd log')
        


TODOs and BUGS
==============
See: http://github.com/dmgctrl/django-ztask/issues
