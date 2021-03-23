# aws-billing-slack-notify

## Abstract
This project executes auto slack notification by using Serverless Application Mode(SAM).

## Build

```bash
$ sam build
```

## Deploy

```bash
$ sam deploy --guided --parameter-overrides SlackWebUrl=[slack webhook URL]

$  Stack Name [sam-app]: NotifyBillingSlack      
$ AWS Region [ap-northeast-1]: 

$ Parameter SlackWebhookUrl [hoge]: {target channel webhook}
$ Image Repository for HelloWorldFunction : {target lambda ecr URI}

$ Confirm changes before deploy [Y/n]: y
$ Allow SAM CLI IAM role creation [Y/n]: y
$ HelloWorldFunction may not have authorization defined, Is this okay? [y/N]: y
$ Save arguments to configuration file [Y/n]: y
$ SAM configuration file [samconfig.toml]: 
$ SAM configuration environment [default]: 
```


