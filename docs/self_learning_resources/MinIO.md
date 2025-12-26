<a id="readme-top"></a>
# MinIO

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#what-is-minio">What is MinIO</a></li>
    <li><a href="#"></a></li>
    <li><a href="#"></a></li>
    <li><a href="#"></a></li>
  </ol>
</details>

## What is MinIO
It's an open source object storage server compatible with Amazon S3. It can be used to store unstructured data like a S3 bucket. It also offers a API compatible with S3, so the changes needed to migrate from S3 to MinIO are minimal. For the data redundancy it offers many options:
* Single Node Single Disk
:::mermaid
graph LR
    N1[Node 1]
    D1[Disk 1]

    N1 --> D1
:::
* Single Node Multiple Disks
:::mermaid
graph LR
    N1[Node 1]
    D1[Disk 1]
    D2[Disk 2]
    D3[Disk 3]

    N1 --> D1
    N1 --> D2
    N1 --> D3
:::
* Distributed Mode (Multiple Nodes with Multiple Disks)
:::mermaid
graph LR
    N1[Node 1]
    N2[Node 2]
    D1[Disk 1]
    D2[Disk 2]
    D3[Disk 3]
    D4[Disk 4]

    N1 --> D1
    N1 --> D2
    N2 --> D3
    N2 --> D4
:::

To store data MinIO uses buckets (S3 buckets), in the buckets you can store objects that can be any type of file. 

## Client configuration
You can manage the MinIO container using the web interface (defined in the `docker-compose.yml` file) or the MinIO client (mc). To use mc you have to configure another container and create an alias.
```bash
# Access the container
docker exec -it <container_name> /bin/sh

# Configure the MinIO alias
mc alias set <ALIAS_NAME> http://<MINIO_HOST>:<MINIO_PORT> <ACCESS_KEY> <SECRET_KEY>
```

Check the information of the MinIO alias
```bash
# Show all aliases
mc alias ls

# Show specific alias
mc admin info <ALIAS_NAME>
```

## Manage users
### Add a user
```bash
mc admin user add <ALIAS_NAME> <USERNAME> <PASSWORD>
# The password must be at least 8 characters long
```

### Show all users
```bash
mc admin user ls <ALIAS_NAME>
```

### Policies
A user can have one or more predefined policy or a custom policy that grants specific permissions.

#### Show all policies
```bash
mc admin policy ls <ALIAS_NAME>
```

#### Get policy details
```bash
mc admin policy info <ALIAS_NAME> <POLICY_NAME>
```

### Assign a policy to a user
```bash
mc admin policy attach <ALIAS_NAME> <POLICY_NAME> --user <USERNAME>
```

### Show assigned policies for a user
```bash
mc admin policy entities <ALIAS_NAME> --user <USERNAME>
```

## Manage buckets
### Create a bucket
```bash
mc mb <ALIAS_NAME>/<BUCKET_NAME>
```

### Show all buckets
```bash
mc ls <ALIAS_NAME>
```

### Show bucket info
```bash
mc ls <ALIAS_NAME>/<BUCKET_NAME>
```

### Show contents of a bucket
```bash
mc ls <ALIAS_NAME>/<BUCKET_NAME>
```

### Remove a bucket
```bash
mc rb <ALIAS_NAME>/<BUCKET_NAME>
```

## Manage files on buckets
### Upload a file
```bash
# Upload a file to a bucket
mc cp <LOCAL_FILE_PATH> <ALIAS_NAME>/<BUCKET_NAME>
# Upload a file to a folder in a bucket
mc cp <LOCAL_FILE_PATH> <ALIAS_NAME>/<BUCKET_NAME>/<FOLDER_NAME>/
# If the folder does not exist, it will be created
```

### Download a file
```bash
mc cp <ALIAS_NAME>/<BUCKET_NAME>/<OBJECT_NAME> <LOCAL_FILE_PATH>
```

### Move a file
```bash
mc mv <ALIAS_NAME>/<BUCKET_NAME>/<OBJECT_NAME> <ALIAS_NAME>/<BUCKET_NAME>/<NEW_OBJECT_NAME>
```

### Show content of a file
```bash
mc cat <ALIAS_NAME>/<BUCKET_NAME>/<OBJECT_NAME>
```

### Remove a file
```bash
mc rm <ALIAS_NAME>/<BUCKET_NAME>/<OBJECT_NAME>
```