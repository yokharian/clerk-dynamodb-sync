# Clerk DynamoDB Sync

![Architecture](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/yokharian/n8n-creative-lab/master/diagram.puml)

Serverless backend that syncs Clerk user data into DynamoDB via webhooks, with JWT-protected API Gateway endpoints. All infrastructure in AWS CDK.

## Tech Stack

- **Runtime**: Python (Lambda)
- **API**: AWS API Gateway (REST)
- **Database**: DynamoDB
- **Auth**: Clerk JWT + webhook signature verification
- **Infrastructure**: AWS CDK
- **CI/CD**: GitHub Actions with integration tests

## How It Works

### Webhook Sync
1. Clerk sends user events (created, updated, deleted) to the webhook endpoint
2. Lambda verifies the webhook signature and processes the event
3. User data is synced to DynamoDB

### Authenticated API
1. Frontend authenticates with Clerk and receives a JWT
2. API Gateway validates the JWT using Clerk's JWKS
3. Lambda handles CRUD operations on DynamoDB

## Features

- Automatic user data sync from Clerk webhooks
- JWT authentication via API Gateway authorizer
- Idempotent webhook processing with conditional writes
- CDK-managed infrastructure with CI/CD
- Integration tests for deployment stability


## References

- [PRD](./prd.md)
- Blog post: [Backend with JWT Authorization](https://yokharian.dev/posts/primeai-webhook-jwt-backend)
