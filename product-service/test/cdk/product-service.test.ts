import * as cdk from 'aws-cdk-lib';
import * as fs from 'fs';
import { Template } from 'aws-cdk-lib/assertions';
import { ProductServiceStack } from '../../lib/product-service-stack';

const app = new cdk.App();
const stack = new ProductServiceStack(app, 'TestProductServiceStack');

const template = Template.fromStack(stack);
const rawData = fs.readFileSync('./lambda-functions/products.json', 'utf8');

test('Number of Lambda functions', () => {
    template.resourceCountIs('AWS::Lambda::Function', 2);
}),

test('Lambda Function getProductsList is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'getProductsList.handler',
        Runtime: 'python3.12',
        FunctionName: 'getProductsList',
        "Environment": {
              "Variables": {
                "MOCK_PRODUCTS": rawData
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
                "MOCK_PRODUCTS": rawData
              }
        }
    });
});

test('API Gateway is Created', () => {
    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
});