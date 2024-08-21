## Deploy Python Lambda functions with container images

Reference: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients

#### The command to build lambda image
```shell
docker build --platform linux/amd64 -t lambda_event_trigger_toturial:latest -f ./lambda/Dockerfile ./lambda
```
or

```shell
cd lambda && 
docker build --platform linux/amd64 -t lambda_event_trigger_toturial:latest .
```

#### The command to run lambda

.env.local
```shell
ENV=dev
AWS_DEFAULT_REGION=ap-southeast-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```


```shell
docker run --platform linux/amd64 --env-file .env.local -p 9000:8080 -it lambda_event_trigger_toturial:latest
```

#### Test Lambda

```shell
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"payload":"hello world!"}'
```

### Deploy Lambda

#### Push AWS ECR

```shell
account_id=932682266260
region=ap-southeast-1
image_name=lambda_event_trigger_toturial
repo_name=${image_name}
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.${region}.amazonaws.com
```

```shell
docker tag ${image_name}:latest ${account_id}.dkr.ecr.${region}.amazonaws.com/${image_name}:latest
docker push ${account_id}.dkr.ecr.ap-southeast-1.amazonaws.com/${image_name}:latest
```


### Deploy Infrastructure

```shell
terraform init
```