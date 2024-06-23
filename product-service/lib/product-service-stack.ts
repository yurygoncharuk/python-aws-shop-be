import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as fs from 'fs';

export class ProductServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const rawData = fs.readFileSync('./lambda-functions/products.json', 'utf8');

    // Lambda function getProductsList
    const getProductsListFunction = new lambda.Function(this, 'getProductsList', {
      functionName: 'getProductsList',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'getProductsList.handler',
      environment: {
        MOCK_PRODUCTS: rawData,
      },
    });

    // Lambda function getProductByID
    const getProductByIDFunction = new lambda.Function(this, 'getProductByID', {
      functionName: 'getProductByID',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda-functions'),
      handler: 'getProductByID.handler',
      environment: {
        MOCK_PRODUCTS: rawData,
      },
    });

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
    productsResource.addMethod('GET', new apigateway.LambdaIntegration(getProductsListFunction));

    const productByIDResource = productsResource.addResource('{product_id}');
    productByIDResource.addMethod('GET', new apigateway.LambdaIntegration(getProductByIDFunction));

    new cdk.CfnOutput(this, 'API_URL', {
      value: api.url,
    })
  }
}
