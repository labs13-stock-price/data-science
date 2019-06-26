# Stak

You can find the project at [Stak](https://stock-price-stripe.herokuapp.com/).

## Contributors


|                                       [Dmitriy Kavayazin](https://github.com/DimaKav)                                        |                                       [Derek Shing](https://github.com/derek-shing)                                        |                                       [Zach Angell](https://github.com/zangell44)                                        |                           
| :-----------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------: |
|                      [<img src="https://media.licdn.com/dms/image/C4E03AQHZzRTbNAG5Ig/profile-displayphoto-shrink_800_800/0?e=1567036800&v=beta&t=8ptDa1tD4wL9516Zt_RcPLoIldi3ue2iLu6xNhRfNws" width = "200" />](https://github.com/DimaKav)                       |                      [<img src="https://github.com/labs13-stock-price/data-science/blob/zangell44-patch-1/img/Image%20from%20iOS.jpg" width = "200" />](https://github.com/derek-shing)                       | [<img src="https://avatars2.githubusercontent.com/u/42625717?s=460&v=4" width = "200" />](https://github.com/zangell44) |
|[<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/DimaKav)            |          [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/derek-shing)           |            [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/zangell44)             |
| [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/dkavyazin/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/derek-shing-29321927/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/zachangell/) |


![MIT](https://img.shields.io/packagist/l/doctrine/orm.svg)
![Python 3.8](https://img.shields.io/badge/python-3.6-blue.svg)

## Project Overview

[Trello Board](https://trello.com/b/tMaSFigP/labs-13-stock-price)

[Product Canvas](https://docs.google.com/document/d/1sErdl9BUTUBLWGJuNJwEJ_Yq9q2HgXrK-gNHbhKKqvA/edit#heading=h.1jaf6eug9n0k)

Stak is a trading platform that integrates sentiment from social media data sources. 

We combine traditional technical trading signals with sentiment analysis, alllowing the user to make more profitable trades.

[Deployed Front End](https://stock-price-stripe.herokuapp.com/)

### Tech Stack

Python

- Dash and Flask for API and Web Applications
- NLTK's VaderSentiment Package for Sentiment Analysis
- Pandas, Numpy, and other packages for data analysis and engineering

AWS Infrastructure

- Elastic Beanstalk for Deployment
- RDS (PostgreSQL)
- Lambda for automation of daily pipeline

### Predictions

**Sentiment Analysis**

Our sentiment analysis model builds on NLTK's VaderSentiment module. To better analyze financial posts, we updated the default model with stock market specific lexicon.

For example, the word "long" is associated with positive sentiment scores in our model, while colloquially it would have little impact on sentiment.

### 2️⃣ Explanatory Variables

-   Explanatory Variable 1
-   Explanatory Variable 2
-   Explanatory Variable 3
-   Explanatory Variable 4
-   Explanatory Variable 5

### Data Sources
🚫  Add to or delete source links as needed for your project


-   [Twitter](https://twitter.com/)
-   [Reddit] (https://www.reddit.com/)
-   [Source 3] (🚫add link to python notebook here)
-   [Source 4] (🚫add link to python notebook here)
-   [Source 5] (🚫add link to python notebook here)

### Python Notebooks

🚫  Add to or delete python notebook links as needed for your project

[Python Notebook 1](🚫add link to python notebook here)

[Python Notebook 2](🚫add link to python notebook here)

[Python Notebook 3](🚫add link to python notebook here)

### 3️⃣ How to connect to the web API

🚫 List directions on how to connect to the API here

### How to connect to the data API

**Reddit Endpoint**

This endpoint contains past reddit sentiment data.

`http://sentiment-app.pjj2rgg23c.us-east-1.elasticbeanstalk.com/reddit/<keyword>/<start-date>/<end-date>`

`keyword` corresponds to stock symbols.

`start-date` and `end-date` are used to return a list of dates and random numbers for sentiment

Example usage

`http://sentiment-app.pjj2rgg23c.us-east-1.elasticbeanstalk.com/reddit/AAPL/20190501/20190530`

## Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a [code of conduct](./code_of_conduct.md.md). Please follow it in all your interactions with the project.

### Issue/Bug Request

 **If you are having an issue with the existing project code, please submit a bug report under the following guidelines:**
 - Check first to see if your issue has already been reported.
 - Check to see if the issue has recently been fixed by attempting to reproduce the issue using the latest master branch in the repository.
 - Create a live example of the problem.
 - Submit a detailed bug report including your environment & browser, steps to reproduce the issue, actual and expected outcomes,  where you believe the issue is originating from, and any potential solutions you have considered.

### Feature Requests

We would love to hear from you about new features which would improve this app and further the aims of our project. Please provide as much detail and information as possible to show us why you think your new feature should be implemented.

### Pull Requests

If you have developed a patch, bug fix, or new feature that would improve this app, please submit a pull request. It is best to communicate your ideas with the developers first before investing a great deal of time into a pull request to ensure that it will mesh smoothly with the project.

Remember that this project is licensed under the MIT license, and by submitting a pull request, you agree that your work will be, too.

#### Pull Request Guidelines

- Ensure any install or build dependencies are removed before the end of the layer when doing a build.
- Update the README.md with details of changes to the interface, including new plist variables, exposed ports, useful file locations and container parameters.
- Ensure that your code conforms to our existing code conventions and test coverage.
- Include the relevant issue number, if applicable.
- You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

### Attribution

These contribution guidelines have been adapted from [this good-Contributing.md-template](https://gist.github.com/PurpleBooth/b24679402957c63ec426).

## Documentation

See [Backend Documentation](https://github.com/labs13-stock-price/backend) for details on the backend of our project.

See [Front End Documentation](https://github.com/labs13-stock-price/frontend) for details on the front end of our project.

