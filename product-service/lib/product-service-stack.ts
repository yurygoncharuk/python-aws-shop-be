import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

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

    // Lambda function getProductsList
    const getProductsListFunction = new lambda.Function(this, 'getProductsList', {
      functionName: 'getProductsList',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'getProductsList.handler',
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
      environment: {
        PRODUCTS_TABLE_NAME: productsTable.tableName,
        STOCKS_TABLE_NAME: stocksTable.tableName,
      },
    });
    createProductFunction.addToRolePolicy(dynamodbPolicy);

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
    productsResource.addMethod(
      'GET',
      new apigateway.LambdaIntegration(getProductsListFunction)
    );
    productsResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(createProductFunction)
    );

    const productByIDResource = productsResource.addResource('{product_id}');
    productByIDResource.addMethod(
      'GET',
      new apigateway.LambdaIntegration(getProductByIDFunction)
    );

    new cdk.CfnOutput(this, 'API_URL', {
      value: api.url,
    })
  }
}
