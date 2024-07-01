import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { ImportServiceStack } from '../../lib/import-service-stack';

const app = new cdk.App();
const stack = new ImportServiceStack(app, 'TestImportServiceStack');

const template = Template.fromStack(stack);
const bucket_name = "rs-school-import-service"

test('S3 Bucket is Created', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
        BucketName: bucket_name,
    });
});

test('Lambda Function importFileParser is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'importFileParser.handler',
        Runtime: 'python3.12',
        FunctionName: 'importFileParser',
        "Environment": {
              "Variables": {
                "IMPORT_BUCKET_NAME": Match.anyValue(),
              }
        }
    });
});

test('Lambda Function importProductsFile is Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
        Handler: 'importProductsFile.handler',
        Runtime: 'python3.12',
        FunctionName: 'importProductsFile',
        "Environment": {
              "Variables": {
                "IMPORT_BUCKET_NAME": Match.anyValue(),
              }
        }
    });
});


test('API Gateway is Created', () => {
    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
});