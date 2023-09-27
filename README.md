# IgPlatform
IG is a financial brokerage company based in Singapore. Their free trading UI is simple, but limited. I wanted to build more complex algorithms for analysing the financial data they provide, and so I created a custom IG platform.

Please note that this is not advised for use by third parties - a more comprehensive and robust platform has been built by a team of developers, and can be found at the following address:

https://trading-ig.readthedocs.io/en/latest/index.html

My custom platform does not support IG's streaming service, as I do not require it for my personal financial analysis.

Please also note that this software has not yet been subjected to rigorous testing.

## Navigation
This project comprises 3 fundamental components - the config file, the API handler, and the IG platform.

### The config file
is used to configure the platform to access your personal account.

### The API handler
uses the config file to act as a go-between, between the user's IG account and their code. It enables simple execution of API requests to any given endpoint of the IG REST API.

### The IG platform
uses the API handler to execute get, post, put, and delete requests to all of the IG REST API endpoints. It handles exceptions returned by the API, enabling users to interact with the APIs using simple functions.

## Project future
I am working on a financial analytics platform that will integrate with the IG data, allowing users to quantitatively analyse financial data and build static visualisations. I do not intend to build a front-end for this, but I may extend it with a dashboard-building tool, which would allow users to build interactive dashboards for more in-depth data visualisation purposes.
