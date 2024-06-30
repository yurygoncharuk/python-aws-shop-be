import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3_notifications from "aws-cdk-lib/aws-s3-notifications";
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";

export class ImportServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket
    const bucketName = "rs-school-import-service"

    const importBucket = new s3.Bucket(this, bucketName, {
      bucketName: bucketName,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

     new cdk.CfnOutput(this, "Bucket", { value: importBucket.bucketName });
    // importBucket.addToResourcePolicy(
    //   new iam.PolicyStatement({
    //     effect: iam.Effect.ALLOW,
    //     actions: ["s3:GetObject"],
    //     resources: [`${importBucket.bucketArn}/*`],
    //     principals: [new iam.AnyPrincipal()],
    //   }),
    // );

    // Lambda function importProductsFile
    const importProductsFileFunction = new lambda.Function(this, 'importProductsFile', {
      functionName: 'importProductsFile',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'importProductsFile.handler',
      environment: {
        IMPORT_BUCKET_NAME: importBucket.bucketName,
      },
    });
    importBucket.grantReadWrite(importProductsFileFunction)
    importBucket.grantPut(importProductsFileFunction)
    importBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["s3:GetObject", "s3.PutObject"],
        resources: [`${importBucket.bucketArn}/*`],
        principals: [],
      }),
    );

    // Lambda function importFileParser
    const importFileParserFunction = new lambda.Function(this, 'importFileParser', {
      functionName: 'importFileParser',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'importFileParser.handler',
      environment: {
        IMPORT_BUCKET_NAME: importBucket.bucketName,
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

    // API Gateway
    const api = new apigateway.RestApi(this, 'ImportServiceAPI', {
      restApiName: 'Import Service',
      description: 'Import Service',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      }
    });
    const importProductsResource = api.root.addResource('import');
    importProductsResource.addMethod('GET', new apigateway.LambdaIntegration(importProductsFileFunction), {
      requestParameters: { 'method.request.querystring.name': true },
      requestValidatorOptions: {
        validateRequestBody: false,
        validateRequestParameters: true,
      },
    });
    new cdk.CfnOutput(this, 'API_URL', {
      value: api.url,
    })
  }
}
