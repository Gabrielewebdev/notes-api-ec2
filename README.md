# Notes API on EC2

Notes API with FastAPI and Docker, reusing the domain and repository
code from notes-api-serverless.

## Verified locally
- Docker image with multi-stage build and non-root user.
- Container health check on GET /health.
- Create, read, list and delete endpoints.
- 11 passing API tests.

The application currently stores notes in memory.
Data is lost when the application restarts.

## Planned AWS infrastructure
Terraform modules for networking and compute, ALB, EC2 Auto Scaling,
ECR, dedicated DynamoDB table, HTTPS, SSM and CloudWatch.
GitHub Actions for CI/CD using OIDC.
