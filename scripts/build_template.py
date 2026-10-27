"""Build a self-contained CloudFormation template; no bundler or SAM required."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = 'PAGE = ' + repr((root / 'index.html').read_text(encoding='utf-8')) + '\n' + (root / 'app.py').read_text(encoding='utf-8')
ref = lambda name: {'Ref': name}
sub = lambda value: {'Fn::Sub': value}
attr = lambda name, value: {'Fn::GetAtt': [name, value]}
template = {
 'AWSTemplateFormatVersion': '2010-09-09',
 'Description': 'SlotRescue bounded demo: HTTP API, Lambda, DynamoDB, SES and optional Bedrock.',
 'Parameters': {
  'OperatorKey': {'Type': 'String', 'NoEcho': True, 'MinLength': 24},
  'Sender': {'Type': 'String'}, 'Recipient': {'Type': 'String'},
  'MailMode': {'Type': 'String', 'Default': 'preview', 'AllowedValues': ['preview', 'ses']},
  'AiMode': {'Type': 'String', 'Default': 'rehearsal', 'AllowedValues': ['rehearsal', 'bedrock']}},
 'Resources': {
  'Table': {'Type': 'AWS::DynamoDB::Table', 'Properties': {'BillingMode': 'PAY_PER_REQUEST', 'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}], 'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}]}},
  'Role': {'Type': 'AWS::IAM::Role', 'Properties': {
   'AssumeRolePolicyDocument': {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Principal': {'Service': 'lambda.amazonaws.com'}, 'Action': 'sts:AssumeRole'}]},
   'Policies': [{'PolicyName': 'DemoRuntime', 'PolicyDocument': {'Version': '2012-10-17', 'Statement': [
    {'Effect': 'Allow', 'Action': ['dynamodb:GetItem', 'dynamodb:PutItem'], 'Resource': attr('Table', 'Arn')},
    {'Effect': 'Allow', 'Action': 'ses:SendEmail', 'Resource': sub('arn:${AWS::Partition}:ses:${AWS::Region}:${AWS::AccountId}:identity/${Sender}'), 'Condition': {'ForAllValues:StringEquals': {'ses:Recipients': [ref('Recipient')]}}},
    {'Effect': 'Allow', 'Action': 'bedrock:InvokeModel', 'Resource': sub('arn:${AWS::Partition}:bedrock:${AWS::Region}::foundation-model/amazon.nova-micro-v1:0')},
    {'Effect': 'Allow', 'Action': ['logs:CreateLogStream', 'logs:PutLogEvents'], 'Resource': sub('arn:${AWS::Partition}:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${AWS::StackName}-app:*')}
   ]}}]}},
  'Function': {'Type': 'AWS::Lambda::Function', 'Properties': {'FunctionName': sub('${AWS::StackName}-app'), 'Runtime': 'python3.13', 'Handler': 'index.handler', 'Role': attr('Role','Arn'), 'Timeout': 29, 'MemorySize': 256,
   'Environment': {'Variables': {'TABLE_NAME': ref('Table'), 'OPERATOR_KEY': ref('OperatorKey'), 'SES_SENDER': ref('Sender'), 'TEST_RECIPIENT': ref('Recipient'), 'MAIL_MODE': ref('MailMode'), 'AI_MODE': ref('AiMode')}}, 'Code': {'ZipFile': source}}},
  'Logs': {'Type': 'AWS::Logs::LogGroup', 'Properties': {'LogGroupName': sub('/aws/lambda/${AWS::StackName}-app'), 'RetentionInDays': 7}},
  'Api': {'Type': 'AWS::ApiGatewayV2::Api', 'Properties': {'Name': sub('${AWS::StackName}-api'), 'ProtocolType': 'HTTP'}},
  'Integration': {'Type': 'AWS::ApiGatewayV2::Integration', 'Properties': {'ApiId': ref('Api'), 'IntegrationType': 'AWS_PROXY', 'IntegrationUri': attr('Function','Arn'), 'PayloadFormatVersion': '2.0'}},
  'Route': {'Type': 'AWS::ApiGatewayV2::Route', 'Properties': {'ApiId': ref('Api'), 'RouteKey': '$default', 'Target': {'Fn::Join': ['/', ['integrations', ref('Integration')]]}}},
  'Stage': {'Type': 'AWS::ApiGatewayV2::Stage', 'Properties': {'ApiId': ref('Api'), 'StageName': '$default', 'AutoDeploy': True, 'DefaultRouteSettings': {'ThrottlingBurstLimit': 5, 'ThrottlingRateLimit': 2}}},
  'Permission': {'Type': 'AWS::Lambda::Permission', 'Properties': {'FunctionName': ref('Function'), 'Action': 'lambda:InvokeFunction', 'Principal': 'apigateway.amazonaws.com', 'SourceArn': sub('arn:${AWS::Partition}:execute-api:${AWS::Region}:${AWS::AccountId}:${Api}/*')}}
 },
 'Outputs': {'Url': {'Value': attr('Api','ApiEndpoint')}, 'FunctionName': {'Value': ref('Function')}, 'TableName': {'Value': ref('Table')}}}
(root / 'template.json').write_text(json.dumps(template, indent=2), encoding='utf-8')
print('Built template.json')
