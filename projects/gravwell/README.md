# Gravwell

_How do the different versions of Gravwell compare to each other? How does Gravwell compare to alternative solutions?_

---

Gravwell is a data storage and analysis platform designed to compete with Splunk. It is simpler to setup and use, offers node-based pricing, and is [open source](https://github.com/gravwell/gravwell).

## Contents
- [Introduction](#introduction)
- [Gravwell Features & Constraints](#gravwell-features--constraints)
- [Comparing Pricing Options](#comparing-pricing-options)
- [Personal Opinions](#personal-opinions)
- [Alternative Solutions](#alternative-software)
- [Additional Notes & References](#additional-notes--references)

---

## Gravwell Components
When taking a look at [Gravwell's system architecture](https://docs.gravwell.io/architecture/architecture.html), you might find the following pieces:
- **Backend**: [Ingest](#ingest),  [Storage](#storage)
- **Frontend**: [Analysis](#analysis), [Search](#search), [Automation](#automation)

### [Ingest](https://docs.gravwell.io/ingesters/ingesters.html)
Gravwell's ingesters "gather incoming data, package it into Gravwell entries, and ship it to Gravwell indexers for storage." Gravwell offers many different [official ingesters](https://docs.gravwell.io/ingesters/ingesters.html#ingesters-list), and the [open-source ingest API](https://github.com/gravwell/gravwell/tree/master/ingest) allows for the creation of your own ingesters.

#### [Tags](https://docs.gravwell.io/ingesters/ingesters.html#tags)
Every piece of data that Gravwell ingests is tagged. Tags allow for easier [search](#search) and [query](#analysis), and categorize incoming data.

### [Storage]()
Storage in Gravwell is handled by indexers, 

### [Analysis]()

### [Search]()

### [Automation]()


## Comparing Pricing Options
### [Software](https://www.gravwell.io/pricing)
Gravwell offers four tiers of pricing options:

#### 1. Community Edition 
**Free**

- limited to one indexer
- must be self-hosted
- [cannot ingest more than 13.9 GB/day](#data-ingest)

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
The free community edition of Gravwell has an ingest limit of 13.9 GB/day. While this should usually be enough for small systems, I ran into issues while trying to migrate existing data. Since I was given 30 GB of data total, it was impossible to ingest it all in one day.

## Personal Opinions
### Mediocre Documentation
While the Gravwell documentation is useable, it seems less extensive or polished than the documentation for comparable services, like Splunk. Specifically, it seems to lack a very comprehensive introduction. While a [training manual](./gravwell_training_5.1.2.pdf) is offered, it only contains information relevant to certification and (in my opinion) lacks sufficient instruction for "getting started".

There is also less of a public user-base on forums such as Stack Overflow, making finding answers for specific issues sometimes a little difficult when compared to other, more widely-used platforms.

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