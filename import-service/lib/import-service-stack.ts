import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3_notifications from "aws-cdk-lib/aws-s3-notifications";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as fs from 'fs';

export class ImportServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket
    const bucketName = "rs-school-import-service"

    const importBucket = new s3.Bucket(this, bucketName, {
      bucketName: bucketName,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      cors: [
        {
          allowedMethods: [
            s3.HttpMethods.PUT,
          ],
          allowedOrigins: ['*'],
          allowedHeaders: ['*'],
        },
      ],
    });

    new cdk.CfnOutput(this, "Bucket", { value: importBucket.bucketName });

    // Import SQS
    const sqsName = "catalogItemsQueue"
    const catalogItemsQueueArn: string = cdk.Fn.importValue(sqsName)
    const catalogItemsQueue = sqs.Queue.fromQueueArn(this, sqsName, catalogItemsQueueArn)

    // Lambdas
    const lambda_timeout = 10

    // Import Lambda function basicAuthorizer
    const lambdaName = "basicAuthorizer"
    const lambdaArn: string = cdk.Fn.importValue(lambdaName)
    const basicAuthorizerFunction = lambda.Function.fromFunctionArn(this, lambdaName, lambdaArn)

    // Lambda function importProductsFile
    const importProductsFileCode = fs.readFileSync('lambda-functions/importProductsFile.py', 'utf-8');
    const importProductsFileFunction = new lambda.Function(this, 'importProductsFile', {
      functionName: 'importProductsFile',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromInline(importProductsFileCode),
      handler: 'index.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment: {
        IMPORT_BUCKET_NAME: importBucket.bucketName,
      },
    });
    importBucket.grantReadWrite(importProductsFileFunction)
    importBucket.grantPut(importProductsFileFunction)

    // Lambda function importFileParser
    const importFileParserCode = fs.readFileSync('lambda-functions/importFileParser.py', 'utf-8');
    const importFileParserFunction = new lambda.Function(this, 'importFileParser', {
      functionName: 'importFileParser',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromInline(importFileParserCode),
      handler: 'index.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment: {
        IMPORT_BUCKET_NAME: importBucket.bucketName,
        SQS_URL: catalogItemsQueue.queueUrl,
      },
    });
    importBucket.grantReadWrite(importFileParserFunction)
    importBucket.grantPut(importFileParserFunction)
    importBucket.grantDelete(importFileParserFunction)
    importBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3_notifications.LambdaDestination(importFileParserFunction),
      { prefix: 'uploaded/' }
    );
    catalogItemsQueue.grantSendMessages(importFileParserFunction)

    // API Gateway
    const api = new apigateway.RestApi(this, 'ImportServiceAPI', {
      restApiName: 'Import Service',
      description: 'Import Service',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: apigateway.Cors.DEFAULT_HEADERS,
      }
    });
    const authorizer = new apigateway.TokenAuthorizer(
      this, 'ImportServiceBasicAuthorizer', {
      handler: basicAuthorizerFunction,
      validationRegex: '^(Basic )(.*)$',
      identitySource: apigateway.IdentitySource.header('Authorization'),
    });
    api.addGatewayResponse("Unauthorized", {
      type: apigateway.ResponseType.UNAUTHORIZED,
      responseHeaders: {
        'Access-Control-Allow-Origin': "'*'",
      },
      statusCode: "401",
      templates: {
        'application/json': '{"message":$context.error.messageString}',
      },
    });
    api.addGatewayResponse("AccessDenied", {
      type: apigateway.ResponseType.ACCESS_DENIED,
      responseHeaders: {
        'Access-Control-Allow-Origin': "'*'",
      },
      statusCode: "403",
      templates: {
        'application/json': '{"message":$context.error.messageString}',
      },
    });

    const importProductsResource = api.root.addResource('import');
    importProductsResource.addMethod('GET', new apigateway.LambdaIntegration(importProductsFileFunction), {
      requestParameters: { 'method.request.querystring.name': true },
      requestValidatorOptions: {
        validateRequestBody: false,
        validateRequestParameters: true,
      },
      authorizationType: apigateway.AuthorizationType.CUSTOM,
      authorizer: authorizer,
    });
    new cdk.CfnOutput(this, 'API_URL', {
      value: api.url,
    })
  }
}
