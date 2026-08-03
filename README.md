# aws-projects

Five AWS builds, all provisioned with Terraform, kept in one repo so the patterns
can be compared side by side.

## Why

I support customers on cloud and CI/CD problems, which means reading other
people's infrastructure under time pressure. The fastest way I've found to get
better at that is to build the same kind of stack myself — once you've wired up
an ALB, an IRSA role or an API Gateway integration by hand, you recognise the
failure mode when someone pastes an error into a ticket.

Each project is a complete stack rather than a snippet, because the interesting
problems live in the wiring between services, not in any single resource.

## The projects

| | What it is | The part worth looking at |
|---|---|---|
| **1** | [Highly available WordPress](cloudsensei-project-1-highly-available-wordpress-app) | Hand-written modules for VPC, Aurora, ElastiCache, EFS, ALB and CloudFront. Remote state in S3 with DynamoDB locking. |
| **2** | [EKS platform](cloudsensei-project-2-eks-workshop) | EKS via `terraform-aws-modules/eks` plus `eks-blueprints-addons`, AWS Load Balancer Controller, and Managed Prometheus + Grafana wired with SigV4 auth. |
| **3** | [MERN book store](cloudsensei-project-3-mern-book-store-app) | A React/Node app with its own `infrastructure/` and a SAM template — the contrast between app-centric and infra-centric deploys. |
| **4** | [Serverless order app](cloudsensei-project-4-serverless-order-app) | Event-driven Lambda with DynamoDB, defined both as Terraform and as a SAM template. |
| **5** | [Serverless CRUD HTTP API](cloudsensei-project-5-serverless-crud-http-api) | API Gateway HTTP API to Lambda to DynamoDB, with the execution role and its inline policy defined next to the routes they serve. |

Project 1's modules are written from scratch. Project 2's cluster configuration
follows AWS's EKS Blueprints, and its `app_modules/` are adapted from the public
[AWS EKS Workshop](https://github.com/aws-samples/eks-workshop-v2) rather than
written by me — the Terraform around them is mine.

## Running any of them

Each project stands alone. Prerequisites are Terraform 1.4+ (project 2 pins
`>= 1.4.2`, project 5 `>= 1.2.0`) and AWS credentials with permission to create
the resources in question.

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

Run `terraform destroy` when you're finished. Projects 1 and 2 both stand up
NAT gateways and managed databases, which cost real money by the hour.

## Notes

- These are labs, not production. They favour a working end-to-end stack over
  hardening: security groups are broader than they should be, and there's no
  multi-account or multi-region story.
- Projects 3, 4 and 5 each carry both a Terraform definition and a SAM template.
  That's deliberate duplication for comparison, not something to copy.
- An earlier commit of project 1 checked `terraform.tfvars` in with a demo
  database password. The file is now gitignored and replaced by
  `terraform.tfvars.example`, but it remains in this repo's history — it was
  never used outside a torn-down lab.
