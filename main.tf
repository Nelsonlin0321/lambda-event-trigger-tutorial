terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.18"
    }
  }

  required_version = ">= 1.2.0"
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.lambda_function_name}-policy"
  role = aws_iam_role.lambda_role.name

  policy = "data.aws_iam_policy_document.${var.lambda_function_name}_policy.json"
}

data "aws_iam_policy_document" "s3_trigger_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogGroup",
      "logs:CreateLogStream"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject"
    ]
    resources = ["arn:aws:s3:::${var.s3_bucket}/*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = ["arn:aws:secretsmanager:${var.region}:${var.account_id}:secret:event_trigger_tutorial_lambda_example_secret"]
  }
}


data "archive_file" "lambda" {
  type        = "zip"
  source_dir = "/lambda_function"
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "s3_trigger_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "lambda_function_payload.zip"
  function_name = "${var.lambda_function_name}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda.lambda_handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime       = "python3.12"
  architectures = ["x86_64"]

  environment {
    variables = {
      env                  = "${var.env}"
    }
  }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_trigger_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.s3_bucket}"
}

resource "aws_s3_bucket_notification" "prod_bucket_notification" {
  bucket = "${var.s3_bucket}" # Replace with your bucket name
  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_trigger_lambda.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_prefix       = "${var.env}/"
    filter_suffix       = ".json"
  }
}