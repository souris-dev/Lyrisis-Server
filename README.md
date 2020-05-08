# Lyrisis Server
Server-side code for the lyrics generation server-client application.

Deploys the model by serving it with Flask.

**Note**: The requirements.txt file does not specify tensorflow==2.2.0 because the Docker container it will
be deployed in already has tensorflow installed.