## E-Heritage Project


### QLD AHPI Dump

Field | Notes |
----- | ---- |
id | 
date created | 
date modified | 
name | 
address | 
town | 
lga | 
state | Always 'QLD'
country | Always 'Australia'
category | Always 'Historic'
sos | 
description | 
latitude | 
longitude | 
url | 




### Midas Heritage

Old URL: http://www.heritage-standards.org.uk/
Old FISH Forum: http://www.fish-forum.info/
New Forum URL: http://fishforum.weebly.com


### Other Projects

http://archaeologydataservice.ac.uk/about/ADSOnline25Europeanprojects


### Architecture

Metadata Harvester  ->  Conversion and Indexing ->  Upload to Index


### Notes

* **SRU:** Search/Retrieve via URL. REST based query syntax and search protocol. Based on the abstract models of Z39.50, but removes much of the complexity. SRW was an earlier protocol, based on WSDL/SOAP/XML, but has been significantly simplified into SRU.

http://www.loc.gov/standards/sru/
http://www.oclc.org/research/activities/srw.html?urlm=160242#sru



* **Z39.50:** International standard client-server, application layer communications protocol for searching and retrieving information from a database of TCP/IP. 

* **OCLC:** Research Centre that has defined SRW/SRU

* **Solr:** Search Index Server based on Lucene

* **JZKit:** Pure java toolset for building advanced search and retrieve applications.

* **OAI:** Open Archives Initiative. http://www.openarchives.org/

* **OAI-PMH:** Protocol for Metadata Harvesting. Low barrier mechanism for repository interoperability. Version 2 specified in 2002.
http://www.openarchives.org/pmh/

What about Atom + Json, Atom Publishing Protocol







### Essential Requirements for Linked Data
 * URI’s for records
 * HTTP 303 (See Other) redirects for Real World Objects
 * Generic records that support Content Negotiation
 * Provision of RDF records as one of the support media types in Content Negotiation
 * Support for URI’s that can directly access the records that
   are delivered as a result of Content Negotiation


OCLC Research - SRW/U - http://www.oclc.org/research/activities/srw.html?urlm=160242




#### UQ Data Collections Registry
http://www.itee.uq.edu.au/eresearch/projects/ands/uq-dcr
https://github.com/uq-eresearch/miletus
https://github.com/uq-eresearch/ods-sru-interface

Atom-PMH
: http://uq-eresearch-spec.github.io/atom-pmh/



## Harvesting Sources

Data source independence

* Make it easy to support additional sources of metadata records
* Not tied to the existing sources of metadata records


Must be supported by the registry data managers. Would be able to provide support with writing an exporter, but not long term support. So something that is relatively simple and similar to their existing systems.



# Data Sources

## Victoria

Contains both places and shipwrecks.

http://vhd.heritage.vic.gov.au/vhd/heritagevic

Available as JSON for each record. There was a CSV list, but it's no longer available.

http://vhd.heritage.vic.gov.au/appmystate

85270 places


## QLD

1600 items.

## NSW
http://www.environment.nsw.gov.au/Heritage/listings/database.htm
http://www.environment.nsw.gov.au/heritageapp/heritagesearch.aspx


27,000 items.

Features:
 * Basic Search
 * Advanced Search
 * Map based search
 * Every item has a unique URL

Can download spatial data from [NSW Spatial Data][http://www.planning.nsw.gov.au/spatial-data-download]



## References


http://datahub.io/dataset?tags=heritage
http://datahub.io/dataset?q=heritage


Facet Forward: Faceted Navigation of Federated Search Results for Cultural Heritage Materials (2007)
http://www.ala.org/lita/sites/ala.org.lita/files/content/conferences/forum/2007/oai-pmh_slides.pdf


[Harvesting Repository Data and OAI-PMH - Repositories Support Project](http://)www.rsp.ac.uk/grow/registration/harvesting/


[OAI-PMH and Syndication](https://dev.livingreviews.org/presentations/mpdl_seminar_oaipmh.html)


http://jakoblog.de/2007/09/28/syndication-and-harvesting-with-rss-atom-oai-pmh-and-sitemaps/


[Overview of Federated Search](http://www.nxtbook.com/nxtbooks/infotoday/enterprisesearchsourcebook09/#/20)

http://federatedsearchblog.com/category/basics/



### A simple tech background of [Federated Search at Texas Heritage](http://web.archive.org/web/20070320082003/http://www.thdi.org/help/4-technical/)

They use a combination of real time searching of remote databases with Z39.50 as well as metadata harvesting.


[List of Metadata Standards - Digital Curation](http://www.dcc.ac.uk/resources/metadata-standards/list?page=2)


[Introduction to MIDAS and FISH - Slides - 2005](http://slideplayer.us/slide/6305/)


**[A Resourceful Alternative to OAI-PMH - 2012](http://hublog.hubmed.org/archives/001955.html)**

[The Directory of Open Access Repositories - OpenDOAR](http://www.opendoar.org/)


# Existing Heritage Federated Search Sites

## [Heritage Gateway](http://www.heritagegateway.org.uk/Gateway/)
 * For all of the UK
 * Quick Search
   + Simple term search
 * Advanced Search
   + Where - Find on Map, search name then click to 
   + What - Search by type, or browseable thesaurus of terms. Site, monument of object types.
 * Real time, doesn't appear to store much harvested metadata.
 * Can show search results on a map
 * Includes links to original source database


## AHIP
 * Federated Search of Australian Heritage Databases
 * Released about 13 years ago
 * Written in Perl
 * Downloads XML metadata dumps from source databases


## [Connected Histories](http://www.connectedhistories.org/)
 * 19th Century Britain
 * Federated search of names, places and dates
 * Save/connect/share within a personal workspace
 * Keyword, Place, Full Name, Date (From/To)
 * Filter on document type, date, free/subscription
 * Performed natural language processing for places, names and dates

## [Canadiana Discovery Portal](http://www.canadiana.ca/en/discovery-portal)
 * Has defined own Canadiana Metadata Repository Format (CMR) in XML to be used internally as an intermediary format.
 * Submissions not required to be in that format.
 * Mostly published media
 * Alows filtering/faceting by keyword/date/language/media/contributor

## [Digital Public Library of America](http://d.la/)
 * Brings together the content of libraries, archives and museums. Written word, works of art and culture, records of America's heritage, efforts and data of science.
 * Keyword search, then filter by date, language, location, subject, contributor, media format
  - Results displayed as list, map or timelime
 * Provides an API for developers and maximally open data.
 * Have defined their own DPLA Metadata Application Profile
 * Modern HTML5 UI, fast, masses of records
 * All Open Source Code, built on open source projects

## Also
 * http://www.pastscape.org.uk/
 * 


## References
 * [Perspectives on SolR/Zebra/SRU/Z39.50](http://www.extradrm.com/blog/?p=195)
  - Library Background
  - Z39.50 is essential for the library community
  - Solr didn't originally support fine grained queries to support Z39.50
  - Can be done now using something like JZKit

 * MASHing metadata: Legacy issues in OAI harvesting from three digital libraries (2013)
  - Wanted to setup a generic system for harvesting metadata using OAI
  - Trialed with 3 sources, all of which had useful extra metadata which had to be dealt with manually.


### Links
 * [A collection of museum, gallery, library, archive, archaeology and cultural heritage APIs, machine-readable, linked and open data services for open cultural data](http://museum-api.pbworks.com/w/page/21933420/Museum%C2%A0APIs)


