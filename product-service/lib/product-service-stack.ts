import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { SubscriptionFilter, Topic } from "aws-cdk-lib/aws-sns";
import { EmailSubscription } from "aws-cdk-lib/aws-sns-subscriptions";
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';

export class ProductServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB tables
    const productsTableName = "products"
    const stocksTableName = "stocks"

    const productsTable = new dynamodb.Table(this, productsTableName, {
      tableName: productsTableName,
      partitionKey: {
        name: "id",
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'title',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PROVISIONED,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const stocksTable = new dynamodb.Table(this, stocksTableName, {
      tableName: stocksTableName,
      partitionKey: {
        name: "product_id",
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PROVISIONED,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // IAM policy
    const dynamodbPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [
        productsTable.tableArn,
        stocksTable.tableArn
      ],
      actions: [
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
      ],
    });

    // SQS
    const sqsName = "catalogItemsQueue"
    const catalogItemsQueue = new sqs.Queue(this, sqsName, {
      queueName: sqsName,   
    });
    new cdk.CfnOutput(this, 'QueueName', { value: catalogItemsQueue.queueName });
    new cdk.CfnOutput(this, 'QueueURL', { value: catalogItemsQueue.queueUrl });
    new cdk.CfnOutput(this, 'QueueARN', {
      value: catalogItemsQueue.queueArn,
      exportName: 'catalogItemsQueue',
    });

    // SNS
    const snsName = "createProductTopic"
    const email_first = "yury.hancharuk@gmail.com"
    const email_second = "yury.goncharuk@gmail.com"
    const createProductTopic = new Topic(this, snsName, {
      topicName: snsName,
    });
    new cdk.CfnOutput(this, 'TopicName', { value: createProductTopic.topicName });

    createProductTopic.addSubscription(
      new EmailSubscription(email_first, {
        filterPolicy: {
          count: SubscriptionFilter.numericFilter({ lessThanOrEqualTo: 5 }),
        },
      }),
    );

    createProductTopic.addSubscription(
      new EmailSubscription(email_second, {
        filterPolicy: {
          count: SubscriptionFilter.numericFilter({ greaterThan: 5 }),
        },
      }),
    );

    // Lambdas
    const lambda_timeout = 10
    // Lambda function getProductsList
    const getProductsListFunction = new lambda.Function(this, 'getProductsList', {
      functionName: 'getProductsList',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'getProductsList.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment: {
        PRODUCTS_TABLE_NAME: productsTable.tableName,
        STOCKS_TABLE_NAME: stocksTable.tableName,
      },
    });
    getProductsListFunction.addToRolePolicy(dynamodbPolicy);

    // Lambda function getProductByID
    const getProductByIDFunction = new lambda.Function(this, 'getProductByID', {
      functionName: 'getProductByID',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'getProductByID.handler',
      environment: {
        PRODUCTS_TABLE_NAME: productsTable.tableName,
        STOCKS_TABLE_NAME: stocksTable.tableName,
      },
    });
    getProductByIDFunction.addToRolePolicy(dynamodbPolicy);

    // Lambda function createProduct
    const createProductFunction = new lambda.Function(this, 'createProduct', {
      functionName: 'createProduct',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'createProduct.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment: {
        PRODUCTS_TABLE_NAME: productsTable.tableName,
        STOCKS_TABLE_NAME: stocksTable.tableName,
      },
    });
    createProductFunction.addToRolePolicy(dynamodbPolicy);

    // Lambda function catalogBatchProcess
    const catalogBatchProcessFunction = new lambda.Function(this, 'catalogBatchProcess', {
      functionName: 'catalogBatchProcess',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'catalogBatchProcess.handler',
      timeout: cdk.Duration.seconds(lambda_timeout),
      environment: {
        SQS_URL: catalogItemsQueue.queueUrl,
        SNS_ARN: createProductTopic.topicArn,
        PRODUCTS_TABLE_NAME: productsTable.tableName,
        STOCKS_TABLE_NAME: stocksTable.tableName,
      },
    });
    catalogBatchProcessFunction.addToRolePolicy(dynamodbPolicy);
    catalogItemsQueue.grantConsumeMessages(catalogBatchProcessFunction);
    catalogBatchProcessFunction.addEventSource(
      new SqsEventSource(catalogItemsQueue, {
        batchSize: 5,
        maxBatchingWindow: cdk.Duration.seconds(10),
      }),
    );
    createProductTopic.grantPublish(catalogBatchProcessFunction);

    // API Gateway
    const api = new apigateway.RestApi(this, 'ProductServiceAPI', {
      restApiName: 'Product Service',
      description: 'Product Service',
      deployOptions: {
        stageName: 'prod',
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    const productsResource = api.root.addResource('products');
    const productModel = new apigateway.Model(this, 'ProductModel', {
      restApi: api,
      modelName: 'ProductModel',
      description: 'Create Product body validation',
      contentType: 'application/json',
      schema: {
        type: apigateway.JsonSchemaType.OBJECT,
        required: ['title', 'description', 'price'],
        properties: {
          title: { type: apigateway.JsonSchemaType.STRING },
          description: { type: apigateway.JsonSchemaType.STRING },
          price: { type: apigateway.JsonSchemaType.NUMBER },
          count: { type: apigateway.JsonSchemaType.NUMBER },
        },
      },
    });

    productsResource.addMethod('GET', new apigateway.LambdaIntegration(getProductsListFunction));
    productsResource.addMethod('POST', new apigateway.LambdaIntegration(createProductFunction), {
      requestValidator: new apigateway.RequestValidator(
        this,
        'CreateProductBodyValidator',
        {
          restApi: api,
          requestValidatorName: 'CreateProductBodyValidator',
          validateRequestBody: true,
        }
      ),
      requestModels: {
        'application/json': productModel,
      },
    });

    const productByIDResource = productsResource.addResource('{product_id}');
    productByIDResource.addMethod('GET', new apigateway.LambdaIntegration(getProductByIDFunction));

    new cdk.CfnOutput(this, 'API_URL', {
      value: api.url,
    })

  }
}
