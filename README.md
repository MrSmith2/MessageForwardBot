Bot for forwarding messages between Twitch and YouTube Live
<h1> Installation </h1>
Go to [Google Developers Console](https://console.cloud.google.com/cloud-resource-manager) and create a new project. <br> <br>
Enable YouTube Data API v3 <br> <br>

Then from the Credentials tab, create a new OAuth Client ID and select the Web Application option. In the "Authorized redirect URIs" section, add the redirect URI you want to use. In the case of this project you will type "http://localhost:5500/" and click Save. <br> <br>

Create a .env file in your project directory and copy/paste the Client ID and Client Secret in the file. <br> <br>

Then Copy & Paste the following commands in your terminal: <br>

```
https://github.com/MrSmith2/MessageForwardBot.git
cd MessageForwardBot
python main.py
```
