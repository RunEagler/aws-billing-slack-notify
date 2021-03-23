# aws-billing

## abstract
This project was created by `sam init` command.


## deploy

```bash
sam build
sam deploy --guided --parameter-overrides SlackWebUrl=[slack webhook URL]
```


## deploy setting

Stack Name [sam-app]: NotifyBillingSlack      
AWS Region [ap-northeast-1]: 

Parameter SlackWebhookUrl [hoge]: {target channel webhook}<br>
Image Repository for HelloWorldFunction : {target lambda ecr URI}<br>

Confirm changes before deploy [Y/n]: y<br>
Allow SAM CLI IAM role creation [Y/n]: y<br>
HelloWorldFunction may not have authorization defined, Is this okay? [y/N]: y<br>
Save arguments to configuration file [Y/n]: y<br>
SAM configuration file [samconfig.toml]: <br>
SAM configuration environment [default]: <br>
