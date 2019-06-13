# stock-dash

Dash app which visualizes prices on a stock chart.

pip install -r requirements.txt

python app.py

## Deployment and Testing

### Building and Running with Docker

To run the application locally, first build the docker container

`docker build --tag stock-dashboard .`

Then, run the container

`docker run -i -t -p 8070:8070 --env-file ./.env stock-dashboard`

`-p` maps a port inside the container to your local machine.

`--env-file` passes your environment variables to the docker container.

- When you want to quit the app locally, use `Ctrl+C` in the command line to quit.

### Deploying to AWS Elastic Beanstalk

See more about the EBCLI [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb3-cmd-commands.html?icmpid=docs_elasticbeanstalk_console).

Please note, in all of the below **stock-dashboard** is a stand in for the name of your application. This name can be changed as necessary.

Initialize the EB docker environment. This only needs to be performed for the first deploy.

`eb init -p docker stock-dashboard`

- This creates an EB application

Test the application locally

`eb local run --port 8070`

- If all works well, deploy to EB.

Create app on EB. This only needs to be performed for the first deploy.

`eb create stock-dashboard -i t2.medium`

- This will take a while to copy over all files. It will give relevant status updates.

If the application has already been created, to deploy a new version

`eb deploy`

Open the app

`eb open`

- Run this to open the URL in your web browser.

To terminate the application when it is not in use

`eb terminate stock-dashboard`
