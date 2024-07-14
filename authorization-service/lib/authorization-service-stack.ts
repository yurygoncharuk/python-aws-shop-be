import * as cdk from 'aws-cdk-lib';
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from 'constructs';
import * as dotenv from "dotenv";
import * as fs from 'fs';

const environment = {};
dotenv.config({ processEnv: environment });

export class AuthorizationServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    dotenv.config();

    // Lambdas
    const lambda_timeout = 10
    // Lambda function basicAuthorizer
    const basicAuthorizerCode = fs.readFileSync('lambda-functions/basicAuthorizer.py', 'utf-8');
    const basicAuthorizerFunction = new lambda.Function(this, 'basicAuthorizer', {
      functionName: 'basicAuthorizer',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromInline(basicAuthorizerCode),
      handler: 'index.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment,
    });
    basicAuthorizerFunction.grantInvoke(new cdk.aws_iam.ServicePrincipal('apigateway.amazonaws.com'));
    
    new cdk.CfnOutput(this, 'FunctionARN', {
      value: basicAuthorizerFunction.functionArn,
      exportName: 'basicAuthorizer',
    });
  }
}
