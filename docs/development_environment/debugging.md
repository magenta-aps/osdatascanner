## Debugging

### Shell access

To access a shell on any container based on the OSdatascanner module
images, run

    docker compose {exec|run} <container name> bash

### Simulating errors

To simulate an unreliable network, the pipeline has a setting
(`pipeline.processor.fail_percentage`) that can be used to cause a certain
fraction of conversion tasks to fail randomly. Setting this value to 100 causes
all conversions to fail; this may be a useful tool for simulating, for example,
the expiry of an API key or client secret mid-scan.

(This is obviously not suitable for use in production, so the system only pays
attention to it if the `DEBUG` variable is also set.)

### Printing Stacktraces

A stacktrace is printed to `stderr` if pipeline components receive `SIGUSR1`.
The scan continues without interruption.

The components must be started using `run_stage` (which they are, through docker compose)

Running the engine in Docker, using the namespace sharing between localhost and
docker:

    docker top os2datascanner-worker-1 # get the `<pid>`of the python process
    kill -USR1 `<pid>`
    docker logs os2datascanner-worker-1


Running the engine locally:

    python -m os2datascanner.engine2.pipeline.run_stage worker ps aux | grep os2datascanner
    kill -USR1 <pid>

!!! warning
      It is not recommended to do so, as that increases the likelyhood of "works on my pc" errors.


### Removing messages from the queue

If a malformed message get published to the queue, one of the`*_collector`s or
engine components might crash when trying to parse the message.

And since messages are only removed from the queue after parsing succeeded and
acknowledged by the consumer (the queues are persistent; restarting `RabbitMQ`
does not clear the queues), you might end up in a crash-loop.

There are two ways to clear the queues:  

1. From the CLI: `docker compose exec queue rabbitmqctl purge_queue <queue name>`

!!! Bonus 
      Use `docker compose exec queue rabbitmqctl list_queues` to see what queues there are and
      their message count.

2. Use the web-interface to `RabbitMQ`, as shortly mentioned in [The Basics](the-basics.md#clone-the-repo-and-get-going),
   to `Purge Messages`  



### PyCharm IDE Debugging

It is possible to debug problems or follow data flows in the code using
breakpoints via an IDE. This section describes this procedure for PyCharm. The
overall procedure is as follows:

1. Start the entire Docker Compose stack.
2. Stop the component you wish to debug.
3. Start the component you wish to debug in PyCharm.

We will here use the `explorer` component as an example for a file scan using
the Samba service - if you perform the procedure on another component and for
another source, the files and configuration changes below may have to be
adjusted accordingly, but the overall principle should be the same.

In the `explorer` case, two configuration changes are required:

1. AMQP hostname and port.
2. Samba UNC. 

The former can be changed by creating
a file similar to `os2datascanner/dev-environment/engine/dev-settings.toml` and
the latter can be changed directly in the admin module in the browser.

The complete list of steps to get it up and running are the following:

1. Create a replacement file for
   `os2datascanner/dev-environment/engine/dev-settings.toml` with this content
   (only the `AMQP_HOST` and `AMQP_PORT` have changed):

        secret_value = "THIS VALUE IS NOT SECRET"
       
        [amqp]
        # Nested amqp settings are picked up by the common amqp utility module
        AMQP_HOST = "localhost"
        AMQP_PORT = 8072
        AMQP_USER = "os2ds"
        AMQP_PWD = "os2ds"
       
        # timeout for requests (in seconds)
        timeout = 20
        ttl = 25
   
    Assume we save this file at `/tmp/my-dev-settings.toml`.

2. Start the Docker Compose stack with (double check that you are using the
   latest version of `docker-compose.yml` where the Docker RabbitMQ port 5672
   has been exposed as port 8072 on `localhost`):
   
         docker compose up -d

3. Stop the `explorer` service:

         docker compose stop explorer

4. Run the usual `quickstart_dev` commands.
5. Login to the admin module and navigate to the
   [Filescanner](http://localhost:8020/filescanners/). Press the "Edit"
   button for the "Lille Samba" and update the `UNC` to
   `//localhost:8139/e2test` (remember to save).
6. (This step is not required for IDE debugging, but it serves as a command
   line example - adjust accordingly to use `pdb`). Activate the Python
   virtual environment (assuming this has already been created and that Python
   requirements have been installed) and navigate to the `src` folder:

         cd path/to/os2datascanner
         source venv/bin/activate
         cd src
         OS2DS_ENGINE_USER_CONFIG_PATH=/tmp/my-dev-settings.toml \
          python -m os2datascanner.engine2.pipeline.run_stage explorer

    The scanner should work as usual, and you can start a scan with a locally
    running (non-Docker) `explorer`.

7. For using the PyCharm IDE you will need to create a run/debug configuration
   corresponding the Python command in the previous step. In PyCharm, click the
   "Run configurations" dropdown and click "Edit Configurations...". Click the
   "+" button (top left corner) and add a new "Python" configuration. Edit the
   configuration to match the Python command above as seen in this screenshot
   (make sure to set module name and parameters, environment variables and
   the working directory):

    ![Run Configuration](./run_conf.png)

8. A debug session can now be started - add some breakpoints and start the run
   using the "Debug" button next to the selected (explorer) run configuration
   in the top right corner. You should be able to follow the flow of data
   through the code, inspect variables and objects and step through the code.
