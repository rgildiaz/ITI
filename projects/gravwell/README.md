# Gravwell

_How do the different versions of Gravwell compare? How does Gravwell compare to alternative solutions?_

---

Gravwell is a data storage and analysis platform designed to compete with Splunk. It is simpler to setup and use, offers node-based pricing, and is [open source](https://github.com/gravwell/gravwell). It can be self-hosted, and it's designed to be able to ingest and store any kind of data. This document will explore Gravwell's structure and capabilities, the differences between different versions of the software, and what makes it different from alternative solutions.

## Contents

- [Gravwell Components](#gravwell-components)
- [Comparing Pricing Options](#comparing-pricing-options)
- [Gravwell Features & Constraints](#gravwell-features--constraints)
- [Personal Opinions](#personal-opinions)
- [Alternative Solutions](#alternative-software)
- [Additional Notes & References](#additional-notes--references)

---

## Gravwell Components

<figure style="
  height: auto; 
  width: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
">
  <img 
    src="../../img/gravwell/gravwell.png"
    style="
      max-height: 400px;
      width: auto;
  " 
    alt="Gravwell Data Flows"
    />
</figure>

When taking a look at [Gravwell's system architecture](https://docs.gravwell.io/architecture/architecture.html), you might find the following pieces:

- **Backend**: [Ingest](#ingest), [Storage](#storage)
- **Frontend**: [Analysis](#analysis), [Search](#search), [Automation](#automation)

The following is a breakdown of some of the basic features of each of these components.

### [Ingest](https://docs.gravwell.io/ingesters/ingesters.html)

Gravwell's ingesters "gather incoming data, package it into Gravwell entries, and ship it to Gravwell indexers for storage." Gravwell offers many different [official ingesters](https://docs.gravwell.io/ingesters/ingesters.html#ingesters-list), and the [open-source ingest API](https://github.com/gravwell/gravwell/tree/master/ingest) allows for the creation of your own. Ingesters feed data to indexers, which are responsible for [storage](#storage).

#### [Tags](https://docs.gravwell.io/ingesters/ingesters.html#tags)

Every piece of data that Gravwell ingests is tagged. Tags allow for easier [search](#search) and [query](#analysis), and categorize incoming data. From the user’s point of view, tags are strings such as “syslog”, “pcap-router”, or “default”. Since tags are used for [querying](#search) later, it can be useful to decide on a consistent naming scheme. For example, the tags for the syslogs of five servers might look like this:

```
syslog-http-server1
syslog-http-server2
syslog-file-server1
syslog-file-server2
syslog-email-server1
```

Since wildcards are allowed in queries, this enables flexible searching. For example, you could search ``tag=syslog-*`` to find all the syslog servers. You can search over all HTTP server logs by specifying ``tag=syslog-http-*``.

### [Storage]()

<figure style="
  height: auto; 
  width: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
">
  <img 
    src="../../img/gravwell/gravwell_indexer.png"
    style="
      max-height: 300px;
      width: auto;
  " 
    alt="An example architecture of a Gravwell indexer"
    />
</figure>

Storage in Gravwell is handled by indexers. 

### [Analysis]()

### [Search]()

### [Automation]()

## Comparing Pricing Options

Gravwell offers many different choices for software edition and support level. These vary in price and functionality.

### [Software](https://www.gravwell.io/pricing)

#### 1. Community Edition

**Free**

- limited to one indexer
- must be self-hosted
- [13.9 GB/day ingest limit](#data-ingest)

#### 2. Pro Edition

**$24,000/node/year**

- all features of Community Edition
- unlimited data ingest
- unlimited ingester endpoints
- unlimited search
- SSO support

#### 3. Enterprise Edition

**$48,000/node/year**

- all features of Pro Edition
- unlimited automations
- distributed web frontends
- online "hot" replication

#### 4. Enterprise Cloud Edition

**$48,000+/year**

- all features of Enterprise edition
- cloud-hosted

### [Support](https://www.gravwell.io/pricing#hs_cos_wrapper_module_16678503781958)

Gravwell also offers three tiers of professional support (pricing for each option is not posted):

#### 1. Basic

- **Response time**: 8 business hours (Severity 1) - 4 business days (Severity 4)

#### 2. Professional

- **Response time**: 3 hours initial response, daily updates (Severity 1) - 3 business days (Severity 4)
- **Training**: Coursework available
- **Designated Account Manager**

#### 3. Premium

- **Response time**: 1 hour initial response, updates every 3 hours (Severity 1) - 2 business days (Severity 4)
- **Training**: included
- **Designated Account Manager**
- **Designated Technical Expert**

## Gravwell Features & Constraints

### Data Ingest

The free community edition of Gravwell has an ingest limit of 13.9 GB/day. While this should usually be enough for small systems, I ran into issues while trying to migrate existing data. Since I had 30 GB of data total, it was impossible to ingest it all in one day.

## Personal Opinions

### Mediocre Documentation

While the Gravwell documentation is useable, it seems less extensive or polished than the documentation for comparable services, like Splunk. Specifically, it seems to lack a very comprehensive introduction. While a [training manual](./gravwell_training_5.1.2.pdf) is offered, it only contains information relevant to certification and (in my opinion) lacks sufficient instruction for "getting started".

There is also less of a public user base on forums such as Stack Overflow, making finding answers for specific issues sometimes a little difficult when compared to other, more widely-used platforms.

### "Ingest Anything"

On their [Gravwell vs Splunk page](https://www.gravwell.io/gravwell-vs-splunk), the makers of Gravwell tout that "[their] platform ingests everything and compromises nothing. Splunk can’t say that." However, it seems like Splunk can also ingest anything.

In the [Splunk Enterprise Docs](https://docs.splunk.com/Documentation/Splunk/9.0.2/Data/WhatSplunkcanmonitor),

## Alternative Software

### [Splunk](https://www.splunk.com)

Gravwell positions its product in [direct competition with Splunk](https://www.gravwell.io/gravwell-vs-splunk). Some main differences are:

- **Pricing Model** - Gravwell offers node-based pricing, while [Splunk offers volume- or compute-based pricing](https://www.splunk.com/en_us/products/pricing/enterprise-platform.html).
- **Search/Query** - Splunk uses a proprietary query language. Gravwell's query language is open source.

### [Grafana](https://grafana.com/)

In my opinion, Grafana handles data visualization and analysis more elegantly than Gravwell. Grafana also offers solutions for [logging](https://grafana.com/logs/), [metrics](https://grafana.com/metrics/), and [tracing](https://grafana.com/traces/).

## Additional Notes & References

- [Gravwell](https://www.gravwell.io/)
- [Gravwell Documentation](https://docs.gravwell.io/)