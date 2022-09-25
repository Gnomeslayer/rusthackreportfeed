Create a twitter account.
Use twitter account to create developer account at https://developer.twitter.com/en/docs/twitter-api

Create a new project and get the twitter bearer token.
Put that token in the config.json file.

For the channel, right click a channel > edit channel > integrations > new webhook > copy url
Put the URL in the config where 'channel' is.

If you want the embed version (in my opinion neater) set embed to true.
If you just want the raw tweet message, set embed to false.

In command line, navigate to the folder you've saved this into,
type: pip install -r requirements.txt
type: python twitter.py

You may get an error "Exception: Cannot get stream (HTTP 503): {"title":"ConnectionException","detail":"Your subscription change is currently being provisioned, please try again in a minute.","connection_issue":"ProvisioningSubscription","type":"https://api.twitter.com/2/problems/streaming-connection%22%7D"

Wait a minute and run again.
