import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { ProductServiceStack } from '../../lib/product-service-stack';

const app = new cdk.App();
const stack = new ProductServiceStack(app, 'TestProductServiceStack');

const template = Template.fromStack(stack);

test('Number of Lambda functions', () => {
    template.resourceCountIs('AWS::Lambda::Function', 4);
}),

test('Lambda Function getProductsList is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'getProductsList.handler',
        Runtime: 'python3.12',
        FunctionName: 'getProductsList',
        "Environment": {
              "Variables": {
                "PRODUCTS_TABLE_NAME": Match.anyValue(),
                "STOCKS_TABLE_NAME": Match.anyValue(),
              }
        }
    });
});

test('Lambda Function getProductByID is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'getProductByID.handler',
        Runtime: 'python3.12',
        FunctionName: 'getProductByID',
        "Environment": {
              "Variables": {
                "PRODUCTS_TABLE_NAME": Match.anyValue(),
                "STOCKS_TABLE_NAME": Match.anyValue(),
              }
        }
    });
});

test('Lambda Function createProduct is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'createProduct.handler',
        Runtime: 'python3.12',
        FunctionName: 'createProduct',
        "Environment": {
              "Variables": {
                "PRODUCTS_TABLE_NAME": Match.anyValue(),
                "STOCKS_TABLE_NAME": Match.anyValue(),
              }
        }
    });
});

test('Lambda Function catalogBatchProcess is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'catalogBatchProcess.handler',
        Runtime: 'python3.12',
        FunctionName: 'catalogBatchProcess',
        "Environment": {
              "Variables": {
                "SQS_URL": Match.anyValue(),
                "SNS_ARN": Match.anyValue(),
                "PRODUCTS_TABLE_NAME": Match.anyValue(),
                "STOCKS_TABLE_NAME": Match.anyValue(),
              }
        }
    });
});

test('Number of DynamoDB Tables', () => {
    template.resourceCountIs('AWS::DynamoDB::Table', 2);
});

test('DynamoDB Table products is Created', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
        TableName: 'products',
    });
});

test('DynamoDB Table stocks is Created', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
        TableName: 'stocks',
    });
});

test('Number of SQS Queues', () => {
    template.resourceCountIs('AWS::SQS::Queue', 1);
});

test('SQS Queue catalogItemsQueue is Created', () => {
    template.hasResourceProperties('AWS::SQS::Queue', {
        QueueName: 'catalogItemsQueue',
    });
});

test('Number of SNS Topics', () => {
    template.resourceCountIs('AWS::SNS::Topic', 1);
});

test('SNS Topic createProductTopic is Created', () => {
    template.hasResourceProperties('AWS::SNS::Topic', {
        TopicName: 'createProductTopic',
    });
});

test('API Gateway is Created', () => {
    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
});