# The Grafana Observability Stack: Grafana, Loki, and Promtail for Data Storage and Analysis

_How do Grafana, Loki, and Promtail handle log aggregation and storage, and how does this compare to_ [_Gravwell_](../gravwell/README.md) _and other alternative solutions?_

<style>
    /* code wrapping for the long error message */
    code {
        white-space : pre-wrap !important;
    }
</style>

---

Developed by [Grafana Labs](https://grafana.com/), the trio of [Grafana](https://grafana.com/grafana/), [Loki](https://grafana.com/logs/), and [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/) form a complete open source monitoring system stack.

## Contents

- [The Observability Stack](#the-observability-stack)
- [Setup - Ubuntu Server](#setup---ubuntu-server)
- [User Experience](#user-experience)
- [Limitations, Drawbacks, & Comparisons to Gravwell](#limitations--drawbacks)
- [Conclusion](#conclusion)
- [Troubleshooting](#troubleshooting)
- [Additional Notes & References](#additional-notes--references)

---

## The Observability Stack

While Grafana Labs' various products can be used separately from each other, I used [Grafana](#grafana), [Loki](#loki), and [Promtail](#promtail) all together for this project, running on the same machine.

Grafana discusses their [Observability Stack](https://grafana.com/about/press/2021/02/17/grafana-labs-introduces-grafana-enterprise-stack/) in various places on their site. Since their open source tools are already designed to work together with minimal setup, I thought it would be easiest to use them this way while testing. However, each component can be used in isolation, instead. While this

### [Grafana](https://grafana.com/docs/grafana/latest/)

Grafana Labs' namesake product is _Grafana_, a visualization and dashboarding software that can be run [from the cloud](https://grafana.com/docs/grafana/latest/introduction/grafana-cloud/) or [hosted locally](https://grafana.com/docs/grafana/latest/introduction/) (with an option to upgrade to an [Enterprise scale](https://grafana.com/docs/grafana/latest/introduction/grafana-enterprise/)). It has rich [integrations for many industry standard data sources](https://grafana.com/docs/grafana/latest/datasources/), including [InfluxDB](https://grafana.com/docs/grafana/latest/datasources/influxdb/), [MySQL](https://grafana.com/docs/grafana/latest/datasources/mysql/), and [PostgreSQL](https://grafana.com/docs/grafana/latest/datasources/postgres/).

### [Loki](https://grafana.com/docs/loki/latest/)

Loki is Grafana Labs' solution to log aggregation. As described in [Loki's documentation](https://grafana.com/docs/loki/latest/fundamentals/overview/), "Loki is a datastore optimized for efficiently holding log data. The efficient indexing of log data distinguishes Loki from other logging systems. **Unlike other logging systems, a Loki index is built from labels, leaving the original log message unindexed**."

Loki also supports its own query language, [LogQL](https://grafana.com/docs/loki/latest/logql/).

### [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/)

Promtail is an open source agent which ships local logs to a Loki instance. Since it is developed by Grafana Labs, it ships ready to use with Loki, and in conjunction, Grafana.

## Setup - Ubuntu Server

During testing, I setup this Grafana stack on an [Intel NUC](#equipment) running [Ubuntu Server 20.04 LTS](#equipment) using the steps outlined below.

### Installation

#### [Grafana](#downloads)

Grafana installation is relatively straightforward, following the guide that is provided. Since the server I set up Grafana on isn't connected to the internet, I downloaded the available [standalone Linux binary](https://grafana.com/grafana/download?edition=oss#:~:text=Standalone%20Linux%20Binaries) to my computer and copied it to the server:

```bash
wget https://dl.grafana.com/oss/release/grafana-9.3.2.linux-amd64.tar.gz
scp grafana-9.3.2.linux-amd64.tar.gz ubuntu@192.168.0.10:~
```

There, it can be unzipped:

```bash
tar -zxvf grafana-9.3.2.linux-amd64.tar.gz
```

To run Grafana, use the `grafana-server` binary:

```bash
./grafana-9.3.2/bin/grafana-server
```

It should start-up with something like this:

```bash
INFO [02-01|17:21:37] Starting Grafana logger=settings version=9.3.2 commit=21c1d14e91 branch=HEAD compiled=2022-12-14T10:40:18Z
INFO [02-01|17:21:37] Config loaded from logger=settings file=/usr/bin/grafana-9.3.2/conf/defaults.ini
...
```

Now, the interface can be accessed on [port 3000](http://localhost:3000).

#### [Loki](#downloads)

Loki can be downloaded from Grafana's [GitHub release page](https://github.com/grafana/loki/releases/). In this case, I downloaded the `loki-linux-amd64.zip` file. Then, it can be copied to the server:

```bash
scp loki-linux-amd64.zip ubuntu@192.168.0.10:~
```

There, unzip it. The executable can be copied to `/usr/bin`:

```bash
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/bin
```

Now, it can be run with:

```bash
loki-linux-amd64
```

Since it was installed as a standalone binary, it will fail without a config file, but this error message at least means that it is working:

```
failed parsing config: config.yaml,config/config.yaml does not exist, set config.file for custom config path
```

#### [Promtail](#downloads)

like [Loki](#loki-1), Promtail can also be downloaded from Grafana's [GitHub release page](https://github.com/grafana/loki/releases/). Find the appropriate release for your system, download, and copy to the server.

```bash
scp promtail-linux-amd64.zip ubuntu@192.168.0.10:~
```

Now, just like the Loki installation, it can be unzipped and moved to `/usr/bin`:

```bash
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/bin
```

Then, it can be run with:

```bash
loki-promtail-amd64
```

Again, it will also fail without a config file since it was installed as a standalone executable:

```
level=info ts=2023-02-01T19:10:30.845273148Z caller=promtail.go:123 msg="Reloading configuration file" md5sum=a3442dc04336603ee20d15b2ddb2e1ba
level=error ts=2023-02-01T19:10:30.845295883Z caller=main.go:167 msg="error creating promtail" error="at least one client config should be provided"
```

### Configuration

Follow the suggested configuration order below. Grafana cannot be configured until Loki is configured, and Loki will not store any data until Promtail is configured to transfer logs to Loki.

#### [Loki](https://grafana.com/docs/loki/latest/configuration/)

Loki needs to be configured to listen for incoming data from Promtail. This can be achieved by editing one of the [example starter files provided by Grafana Labs](https://grafana.com/docs/loki/latest/configuration/examples/).

For more information about configuration, visit the [Loki documentation](https://grafana.com/docs/loki/latest/configuration/).

This project used the following config:
```ini
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /data/loki/index

  filesystem:
    directory: /data/loki/chunks

limits_config:
  ingestion_rate_mb: 8

ruler:
  alertmanager_url: http://localhost:9093
```

#### [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/configuration/)

Since Promtail is an agent for Loki, it should be configured to send logs to Loki's intake address. Similar to Loki, [Grafana Labs also provides some example configs in the documentation](https://grafana.com/docs/loki/latest/clients/promtail/configuration/#example-static-config).

Visit the Promtail docs for [more information about configuration](https://grafana.com/docs/loki/latest/clients/promtail/configuration).

This is the config used for this project:
```ini
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
- job_name: system
  static_configs:
  - targets:
      - localhost
    labels:
      job: varlogs
      __path__: /var/log/*log
  - targets:
      - localhost
    labels:
      job: syslogs
      __path__: /home/shredos/gravwell/syslog-archive/*.gz
  - targets:
      - localhost
    labels:
      job: siabmgr
      __path__: /usr/home/shredos/gravwell/siabmgrCCC/*
```

#### Grafana

Grafana can be fully configured through the web UI. By default, it runs on [port 3000](http://localhost:3000).

## User Experience

## Limitations, Drawbacks, & Comparisons to Gravwell

### Setup Time & Scaling

One of the advantages of Gravwell is its ease of use. Instead of needing to setup an entire stack, Gravwell can be used from a single binary, running on one management device. Grafana, on the other hand, requires separate manual setup of the frontend, backend, and any ingestion agents (in this case, any Promtail instances).

While this may be a benefit in a situation that requires scalability, allowing for separate scaling of each component of the stack as necessary, [Gravwell can also be run as a distributed system](https://docs.gravwell.io/architecture/architecture.html). In addition to each component of the Grafana stack being capable of separate deployment, [Loki can be run in "microservices mode"](https://grafana.com/docs/loki/latest/fundamentals/architecture/deployment-modes/), which allows for each of its components to be deployed as a microservice.

## Conclusion

## Troubleshooting

### Port 3100 in use

When I first worked to get Grafana, Loki, and Promtail running, I kept running into an issue with Loki. After

### Loki Ingestion Rate Limit

Unlike Gravwell, Promtail/Loki don't have a dedicated log migration tool. Instead, the suggested method for migrating large amounts of logs is to point Promtail at their location on your device. While the OSS Grafana stack no daily ingest limit like [Gravwell has](../gravwell/README.md#data-ingest), importing logs can be a little slow by default, leading to a backup of importing files with continuous error messages like this:

```bash
level=warn ts=2023-02-01T17:48:53.313036925Z caller=client.go:379 component=client host=localhost:3100 msg="error sending batch, will retry" status=429 error="server returned HTTP status 429 Too Many Requests (429): Ingestion rate limit exceeded for user fake (limit: 4194304 bytes/sec) while attempting to ingest '6510' lines totaling '1048430' bytes, reduce log volume or contact your Loki administrator to see if the limit can be increased"
```

Loki has a [default ingestion rate of 4 MB/sec/user](https://grafana.com/docs/loki/latest/configuration/#limits_config:~:text=%5Bingestion_rate_mb%3A%20%3Cfloat%3E%20%7C%20default%20%3D%204%5D). In this case, the ingestion rate was slightly above the limit. This can be configured with the [`limits_config`](https://grafana.com/docs/loki/latest/configuration/#limits_config) block of your Loki config file. In this case, the issue was resolved by doubling the ingestion rate-limit with this block in my config:

```
limits_config:
  ingestion_rate_mb: 8
```

## Additional Notes & References

### Downloads

- [Grafana OSS](https://grafana.com/grafana/download?edition=oss)
- [Loki (run locally)](https://grafana.com/docs/loki/latest/installation/local/)
- [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/installation/)

### Equipment

- [Intel NUC](https://ark.intel.com/content/www/us/en/ark/products/95067/intel-nuc-kit-nuc7i5bnh.html)
- [Ubuntu 20.04](https://releases.ubuntu.com/20.04/)
