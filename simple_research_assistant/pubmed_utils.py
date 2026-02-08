"""
Simple PubMed Search Utility - OPTIMIZED
"""
import requests
from typing import List, Dict
from config import config


def search_pubmed(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search PubMed for papers - OPTIMIZED with abstracts
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of paper dictionaries with abstracts
    """
    try:
        # Step 1: Search for IDs
        search_url = f"{config.PUBMED_BASE_URL}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "email": config.PUBMED_EMAIL
        }
        
        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        ids = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not ids:
            return []
        
        # Step 2: Fetch details with abstracts
        fetch_url = f"{config.PUBMED_BASE_URL}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
            "rettype": "abstract",
            "email": config.PUBMED_EMAIL
        }
        
        response = requests.get(fetch_url, params=fetch_params, timeout=15)
        response.raise_for_status()
        
        # Parse XML
        papers = parse_pubmed_xml(response.text)
        
        return papers
    
    except Exception as e:
        print(f"PubMed search error: {e}")
        return []


def parse_pubmed_xml(xml_text: str) -> List[Dict]:
    """Parse PubMed XML response"""
    import xml.etree.ElementTree as ET
    
    papers = []
    
    try:
        root = ET.fromstring(xml_text)
        
        for article in root.findall('.//PubmedArticle'):
            try:
                # Get article data
                medline = article.find('.//MedlineCitation')
                article_elem = medline.find('.//Article')
                
                # PMID
                pmid = medline.find('.//PMID').text
                
                # Title
                title = article_elem.find('.//ArticleTitle').text or ""
                
                # Authors
                authors = []
                author_list = article_elem.find('.//AuthorList')
                if author_list is not None:
                    for author in author_list.findall('.//Author')[:3]:
                        lastname = author.find('.//LastName')
                        forename = author.find('.//ForeName')
                        if lastname is not None:
                            name = lastname.text
                            if forename is not None:
                                name = f"{forename.text} {name}"
                            authors.append(name)
                
                # Abstract
                abstract = ""
                abstract_elem = article_elem.find('.//Abstract/AbstractText')
                if abstract_elem is not None:
                    abstract = abstract_elem.text or ""
                
                # Journal
                journal = ""
                journal_elem = article_elem.find('.//Journal/Title')
                if journal_elem is not None:
                    journal = journal_elem.text or ""
                
                # Publication date
                pubdate = ""
                pubdate_elem = article_elem.find('.//Journal/JournalIssue/PubDate/Year')
                if pubdate_elem is not None:
                    pubdate = pubdate_elem.text
                
                # DOI
                doi = ""
                for eloc in article_elem.findall('.//ELocationID'):
                    if eloc.get('EIdType') == 'doi':
                        doi = eloc.text
                        break
                
                paper = {
                    "pmid": pmid,
                    "title": title,
                    "authors": authors if authors else ["Unknown"],
                    "abstract": abstract,
                    "journal": journal,
                    "pubdate": pubdate,
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "doi": doi
                }
                papers.append(paper)
            
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        return papers
    
    except Exception as e:
        print(f"XML parsing error: {e}")
        return []


# Add to config if not present
if not hasattr(config, 'PUBMED_BASE_URL'):
    config.PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
