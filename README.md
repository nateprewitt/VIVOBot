VIVOBot
--------------

VIVOBot is a simple python class used to perform basic actions in VIVO via a scripting interface.

This will allow you to do things like run inference, upload an ontology file, or perform queries with a cronjob.

You can also use this to perform quick data retrievals out of VIVO for data mashups or complex processing that you
would prefer to do in a programming environment.

##Setup
    * Install [VIVO](https://github.com/vivo-project/VIVO)
    * Download [VIVOBot](https://github.com/nateprewitt/VIVOBot)
    * Create your config file. You can see an example [here](https://github.com/nateprewitt/VIVOBot/blob/master/config/vivobot.cfg.example).
    * You're ready to start building!

##Usage

    VIVOBot currently has a small number of basic functions in the VIVO UI but has helped automate things that otherwise required manual action. VIVOBot can be used in two ways for whatever purposes you can think of. Either write some python and create an instance of VIVOBot with a simple import, or use the CLI file to automate tasks from the command line. If you choose to use the command line route, there's a bit of setup required that I'll address below.

    The python vb_cli.py takes up to 3 parameters which will invoke an instance of VIVOBot and process a supplied *task* file. The *task* file is a chronological set up commands for VIVOBot to perform. You can find an example file [here](https://github.com/nateprewitt/VIVOBot/blob/master/tasks/example.task).

    Here is an example use of vb_cli.py:

    <pre>
        python vb_cli.py config/vivbot.cfg tasks/generate_reports.task
    </pre>

    Responses from the server with query results, etc. will be written to the logs directory for retrieval. There currently isn't a way to specify a custom logging directory but we'll look into that for future versions.
