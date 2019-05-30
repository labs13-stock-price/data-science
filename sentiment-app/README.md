# Data Science Flask Application Guide


## API Endpoints

### Test Endpoint

This endpoint is for use during development.

`http://sentiment-app.pjj2rgg23c.us-east-1.elasticbeanstalk.com/test/<keyword>/<start-date>/<end-date>`

`keyword` doesn't do anything for the test endpoint

`start-date` and `end-date` are used to return a list of dates and random numbers for sentiment

Example usage

`http://sentiment-app.pjj2rgg23c.us-east-1.elasticbeanstalk.com/test/keyword/20190501/20190530`


### Twitter Endpoint

TO-DO


## Deployment and Testing

### Building and Running with Docker

To run the application locally, first build the docker container

`docker build --tag sentiment-app .`

Then, run the container

`docker run -i -t -p 5000:5000 --env-file ./.env sentiment-app`

`-p` maps a port inside the container to your local machine.

`--env-file` passes your environment variables to the docker container.

- When you want to quit the app locally, use `Ctrl+C` in the command line to quit.

### Deploying to AWS Elastic Beanstalk

See more about the EBCLI [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb3-cmd-commands.html?icmpid=docs_elasticbeanstalk_console).

Please note, in all of the below **sentiment-app** is a stand in for the name of your application. This name can be changed as necessary.

Initialize the EB docker environment. This only needs to be performed for the first deploy.

`eb init -p docker sentiment-app`

- This creates an EB application

Test the application locally

`eb local run --port 5000`

- If all works well, deploy to EB.

Create app on EB. This only needs to be performed for the first deploy.

`eb create sentiment-app`

- This will take a while to copy over all files. It will give relevant status updates.

If the application has already been created, to deploy a new version

`eb deploy`

Open the app

`eb open`

- Run this to open the URL in your web browser.

To terminate the application when it is not in use

`eb terminate sentiment-app`