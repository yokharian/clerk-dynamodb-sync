# 🧠 PRD: Clerk DynamoDB Sync

## tl;dr

Serverless backend that synchronizes external user data into DynamoDB through Clerk webhooks, with JWT authentication via API Gateway protecting REST endpoints. All infrastructure defined in AWS CDK with CI/CD and integration tests.

---

## 🎯 Goals

- **Webhook-Driven Sync**: Automatically sync user data (create, update, delete) from Clerk into DynamoDB via webhook events
- **JWT Authentication**: Secure API Gateway endpoints using JWT tokens issued by Clerk
- **Serverless Architecture**: Run entirely on Lambda + API Gateway, eliminating server management overhead
- **Infrastructure as Code**: AWS CDK manages all resources for reproducible deployments
- **CI/CD**: Automated deployment pipeline with integration tests to ensure stability

## 👤 User Stories

- As a **frontend developer**, I want to authenticate via Clerk and call backend APIs so I can access protected user data
- As a **system**, I want user data changes in Clerk to automatically sync to DynamoDB so the database stays current without manual intervention
- As a **backend developer**, I want JWT validation on API Gateway so unauthorized requests are rejected before reaching Lambda
- As a **DevOps engineer**, I want CDK-managed infrastructure so I can deploy and tear down environments consistently

## 🔄 Data Flow

### Webhook Sync Flow

```text
1. User data changes in Clerk (created, updated, deleted)
   ↓
2. Clerk sends webhook event to API Gateway endpoint
   ↓
3. Webhook Lambda verifies Clerk signature
   ↓
4. Lambda processes event type (user.created, user.updated, user.deleted)
   ↓
5. Lambda writes/updates/deletes record in DynamoDB
   ↓
6. Response: 200 OK to Clerk webhook
```

### Authenticated API Flow

```text
1. Frontend authenticates with Clerk, receives JWT
   ↓
2. Frontend sends request to API Gateway with Bearer token
   ↓
3. API Gateway validates JWT using Clerk's JWKS
   ↓
4. If valid: request forwarded to Lambda
   ↓
5. Lambda reads/writes DynamoDB
   ↓
6. Response returned to frontend
```

## 🧱 Core Components

### API Gateway

- **Webhook Endpoint** (`POST /webhooks/clerk`): Receives Clerk webhook events, no auth (signature verification instead)
- **User Endpoints** (`GET/POST /users`): Protected by JWT authorizer
- **Health Check** (`GET /health`): Unauthenticated service health endpoint

### Lambda Functions

- **Webhook Handler**: Verifies Clerk webhook signature, parses event type, writes to DynamoDB
- **User API Handler**: CRUD operations on user records in DynamoDB, protected by JWT

### Data Store

- **DynamoDB Table**: Users table with `user_id` as partition key
  - Stores synced Clerk user data (email, name, metadata)
  - Supports conditional writes for idempotency

### Infrastructure (CDK)

- **API Gateway**: REST API with JWT authorizer using Clerk's JWKS URL
- **Lambda Functions**: Webhook and user API handlers
- **DynamoDB Table**: Users table with point-in-time recovery
- **CI/CD Pipeline**: Automated deploy on push with integration tests

## 📚 References

- [Architecture Diagram](./diagram.puml)
- Blog post: [Backend with JWT Authorization](https://yokharian.dev/posts/primeai-webhook-jwt-backend)