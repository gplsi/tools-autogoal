
# tools-autogoal

This project configures a Docker-based deployment of [AutoGOAL-UI](https://github.com/jlm111-ua/autogoal) which developed a graphical user interface for [AutoGOAL](https://github.com/autogoal/autogoal). 


To deploy:
- navigate to `./docker`  folder
- ensure that `./docker/gui/startup/entrypoint.sh` and `./docker/gui/startup/entrypoint.sh` has execution privileges.
- run docker-compose up -d

In brief, we deploy two containers:
- **gplsi-autogoal-gui**: web app HTML + JavaScript + FastAPI. The container has:
	- nginx to handle requests.
	- FastAPI as a service using supervisor.

- **gplsi-autogoal-server**: back-end that handles the integration with AutoGOAL. FastAPI services are deployed similarly to gplsi-autogoal-gui.
