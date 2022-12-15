# Gravwell

_How do the different versions of Gravwell compare to each other? How does Gravwell compare to alternative solutions?_

---

## Contents
- [Introduction](#introduction)
- [Gravwell Features & Constraints](#gravwell-features--constraints)
- [Comparing Pricing Options](#comparing-pricing-options)
- [Personal Opinions](#personal-opinions)
- [Alternative Solutions](#alternative-software)
- [Additional Notes & References](#additional-notes--references)


## Introduction

## Comparing Pricing Options
### [Software](https://www.gravwell.io/pricing)
Gravwell offers four tiers of pricing options for the service itself:

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
### Ingest Anything
While other services like [Splunk](#splunk) can only ingest 

The free community edition of Gravwell has an ingest limit of 13.9 GB/day. While this should usually be enough for small systems, I ran into issues while trying to migrate existing data. Since I was given 30 GB of data total, it was impossible to ingest it all in one day.

## Personal Opinions
### Weak Documentation
While the Gravwell documentation is serviceable, it seems less extensive or polished than the documentation for comparable services, like Splunk.

### "Ingest Anything"
On their [Gravwell vs Splunk page](https://www.gravwell.io/gravwell-vs-splunk), the makers of Gravwell tout that "[their] platform ingests everything and compromises nothing. Splunk can’t say that." However, it seems like Splunk can also ingest anything.

In the [Splunk Enterprise Docs](https://docs.splunk.com/Documentation/Splunk/9.0.2/Data/WhatSplunkcanmonitor), 


## Alternative Software
### Splunk
Gravwell positions its product in [direct competition with Splunk](https://www.gravwell.io/gravwell-vs-splunk). Some main differences are:
- **Pricing Model** - Gravwell offers node-based pricing, while [Splunk offers volume- or compute-based pricing](https://www.splunk.com/en_us/products/pricing/enterprise-platform.html).
- **Data Ingest** - 

## Additional Notes & References
- [Gravwell](https://www.gravwell.io/)