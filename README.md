# STM-CLI-Feed-Example
 Example


## Setup and Pre-requisites

1. If not already installed:

- Install Docker on your device (you can use the following link for a guide: <https://docs.docker.com/get-docker/>)
- Install Solace Try-Me CLI (stm) (You can find an installation guide here: <https://docs.solace.com/Get-Started/tutorial/try-me-cli-tool.htm>)
- Install WSL 2 if looking to use stm cli with a Windows System (You can find an instalation guide here: <https://learn.microsoft.com/en-us/windows/wsl/install>)

2. Clone this repository or download the .zip file from GitHub (extract the downloaded zip file)

## Dockerized Deployment

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Change directory to `Solace_docker-compose` using the following command:

    ```
    cd Solace_docker-compose
    ```

3. Run the following command: 

    ```
    docker-compose up --build -d
    ```

    This will take some time to complete, allow for 30 seconds to a full minute.

4. the following 2 containers should now be running and/or have finnished running:
    - `solace`: The Solace PubSub+ message broker
    - `solace-init`: where a python script runs to set up our solace container for the testing payment solution. This container will exit after it has completed its intended purpose

## Verifying Deployment 

Once deployed, the Solace broker should be accessible through it's web console at <http://localhost:8081>:

1. When greeted with the initial login page, use the credentials defined in the solace container's environment variables as defined in the `docker-compose.yml` file (line 54 & 55).

2. Once logged in, the `default` Message VPN card should show there are 6 queues and topic endpoints. Click on the `default` Message VPN Card

3. Using the left column, navigate to `Queues`: You should see 6 Queues.

## **Using Solace Try-Me CLI for mocking**

For this project, we highly recommend using the pre-generated feed provided, though a guide is provided below for generating a new stm feed using the provided asyncapi file (test-banking-0.1.0.json). 

Skip to [this section](#running-a-feed-using-stm-cli) if you are content with only using the provided stm feed.

## Generating a new Feed from an Asyncapi file

1. Open a cli window where stm is accessible. You can verify this with the following command: 
    ```
    stm -v
    ```
2. Run the following command: 
    ```
    stm feed generate
    ```

3. Choose the feed type as `asyncapi_feed`

4. Enter the path to the asyncapi file in your cloned repository. If using WSL on Windows, copy the file to WSL and use its file path instead.

5. Proceed with filling each field when prompted.

    When successful, stm will return the following:
    ```
    ✔  success   success: Successfully created event feed <name you gave to new feed>
    ✔  success   success: exiting...
    ```

6. Using the file explorer on your machine, navigate to the `.stm` directory generated during your installation of stm cli, then navigate into the `feeds` directory/folder. 

7. Inside, you should see a directory/folder with the name of the feed you just generated. Navigate into this directory.

8. You should see 6 json files:
    * analysis.json
    * fakerrules.json
    * feedinfo.json
    * feedrules.json
    * feedschemas.json
    * The asyncapi file used to generate this feed

While you have generated a new feed to be used with stm cli, it will not work as intended in it's current state. If you compare and contrast the `feedrules.json` file in the feed you have generated with the one provided in this repository:
* In the feed you generated, every topic's `publishSettings` object has the same value:
    ```json
    "publishSettings": {
        "count": 0,
        "interval": 1000,
        "delay": 0
    }
    ```
    This will mean that if you attempt to run the newly generated feed, not only will it not send any events to your Solace Broker, it will take a 1000 seconds (16 minutes and 40 seconds) before stm completes the command without sending any events. 
    
    <ins>**These need to be changed**</ins> for the new feed to be useful. 

    Here is an example of a `publishSettings` value that sends 10 events every second: 
    ```json
    "publishSettings": {
        "count": 10,
        "interval": 1,
        "delay": 0
    }
    ```
* The `topicParameters` and `payload` fields for each topic will be different between the newly generated feed and the one provided. Notice how in the new feed, topic parameters and payload values are defined in very similar ways: 
    * String values are all defined as follows:
        ```json
        "<name of value>": {
            "description": "<description provided by asyncapi source file>",
            "type": "string",
            "rule": {
                "description": "<description provided by asyncapi source file>",
                "type": "string",
                "name": "<name of value>",
                "group": "StringRules",
                "rule": "alpha",
                "casing": "mixed",
                "minLength": 10,
                "maxLength": 10
            }
        }
        ```
    * Numerical values are all defined as follows:
        ```json
        <!-- Integer Values -->

        "<name of value>": {
            "description": "<description provided by asyncapi source file>",
            "type": "integer",
            "rule": {
                "description": "<description provided by asyncapi source file>",
                "type": "integer",
                "name": "<name of value>",
                "group": "NumberRules",
                "rule": "int",
                "minimum": 0,
                "maximum": 1000
            }
        }

        <!-- Floating Point Values -->

        "<name of value>": {
            "description": "<description provided by asyncapi source file>",
            "type": "number",
            "rule": {
                "description": "<description provided by asyncapi source file>",
                "type": "number",
                "name": "<name of value>",
                "group": "NumberRules",
                "rule": "float",
                "minimum": 0,
                "maximum": 1000,
                "fractionDigits": 2
            }
        }
        ```
    These are the default definitions for payload values and topic parameters (with a few differences) for events created by a newly generated feed when run.

    While these do not need to be changed for the feed to run successfully, these default values may not reflect the real world examples you may want to mock. It's not a bad thing for a timestamp to be stored as a string, but the default definition for a string will most likely not return a value that looks like a date.

    Fortunately, the `fakerrules.json` file provides a list of alternate rules to define generation rules topic parameter and payload values. You can also use the provided feed as well as Solace's own repository of comunity feeds (<https://github.com/solacecommunity/solace-event-feeds>) as examples and/or references to make your feed generate more useful mock events.

## Running a feed using STM CLI

To make sure stm will send messages to the broker you just deployed:

* Change stm connection settings by running the following command (replace username and password with the credentials used to login to the broker's web console):
    ```
    stm manage connection -u "username" -p "password"
    ```

To make sure you can run the provided feed:

1. Locate the `.stm` directory created when installing stm cli on to your local machine.

2. Copy the `Test-Banking` folder in your cloned repository into the `.stm/feeds` directory.


To run the provided feed (or any feed you have locally on your machine):

1. Run the following command: 
    ```
    stm feed run -feed "Test-Banking"
    ```

    If you want to run a different locally stored feed, replace `"Test-Banking"` with the name of the feed you want to run.

2. When prompted to select which topic to publish to, press enter to publish events to all topics.

3. As the feed is being run, you will see a stream of messages being published. 

4. You can verify the messages are being received by the Solace Broker through its web console:
    * The `Fraud` Queue should have received 10 messages
    * The `AI` Queue should have received 10 messages
    * The sum total of messages in each queue corresponding to a bank should be 100 messages
