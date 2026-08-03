# aws-projects

Three AWS builds, provisioned with Terraform, kept in one repo so the patterns
can be compared side by side.

## Why

I support customers on cloud and CI/CD problems, which means reading other
people's infrastructure under time pressure. The fastest way I've found to get
better at that is to build the same kind of stack myself — once you've wired up
an ALB, an execution role or an API Gateway integration by hand, you recognise
the failure mode when someone pastes an error into a ticket.

Each project is a complete stack rather than a snippet, because the interesting
problems live in the wiring between services, not in any single resource.

## The projects

| | What it is | The part worth looking at |
|---|---|---|
| **1** | [Highly available WordPress](cloudsensei-project-1-highly-available-wordpress-app) | Hand-written modules for VPC, Aurora, ElastiCache, EFS, ALB and CloudFront. Remote state in S3 with DynamoDB locking. |
| **3** | [MERN book store](cloudsensei-project-3-mern-book-store-app) | A React/Node app containerised for ECS, with its own `infrastructure/` and GitHub Actions for plan and apply. |
| **5** | [Serverless CRUD HTTP API](cloudsensei-project-5-serverless-crud-http-api) | API Gateway HTTP API to Lambda to DynamoDB. The handlers are the most finished code here — explicit status codes, scoped IAM, no runtime table discovery. |

The numbering has gaps because two projects were removed: an EKS build that was
mostly AWS's own workshop content rather than mine, and a serverless order app
that was abandoned half-finished and never validated.

## Running any of them

Each project stands alone. Prerequisites are Terraform 1.2+ and AWS credentials
with permission to create the resources in question.

```bash
cd cloudsensei-project-1-highly-available-wordpress-app
cp terraform.tfvars.example terraform.tfvars   # then edit
terraform init
terraform plan
terraform apply
```

Two things to change before the first apply: the S3 bucket names in
`terraform.tfvars` must be globally unique, and secrets are read from the
environment rather than from a file —

```bash
export TF_VAR_db_password="$(openssl rand -base64 24)"
```

Project 5 packages its Lambdas before applying — see
[`scripts/bash/create.sh`](cloudsensei-project-5-serverless-crud-http-api/scripts/bash/create.sh),
which zips each handler, uploads it to S3 and then runs Terraform.

Run `terraform destroy` when you're finished. Project 1 stands up NAT gateways
and an Aurora cluster, which cost real money by the hour.

## Notes

- These are labs, not production. They favour a working end-to-end stack over
  hardening: there's no multi-account or multi-region story, and project 1's
  security groups are broader than they should be.
- Secrets are read from the environment or from gitignored files, with a
  `.example` committed alongside each: `terraform.tfvars.example` in projects 1
  and 5, and a `.env.example` per service in project 3.
- Early commits did check in a database password and a Mongo Atlas URI. Those
  values have been purged from the history and the branches force-pushed, so
  the old commits now read `REDACTED` and a placeholder. Neither was used
  outside a lab that no longer exists.
