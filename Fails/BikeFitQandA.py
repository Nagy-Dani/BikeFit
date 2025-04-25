import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from nltk.tokenize import sent_tokenize
import nltk
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bike_fit_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Download NLTK data for sentence tokenization
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class BikeFitScraper:
    """Optimized scraper for Bike Fit Adviser website."""
    
    def __init__(self, base_url="https://www.bikefitadviser.com"):
        self.base_url = base_url
        self.blog_url = f"{base_url}/blog"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.articles = []
        self.session = requests.Session()
    
    def get_all_blog_urls(self, max_pages=20, start_offset=1486856971000):
        """
        Scrapes all blog post URLs from the blog index pages.
        Uses the offset parameter from the URL structure.
        """
        blog_urls = []
        current_offset = start_offset  # Start with the provided offset
        
        for page in range(max_pages):
            if page == 0:
                url = self.blog_url
            else:
                url = f"{self.blog_url}?offset={current_offset}"
            
            logger.info(f"Scraping blog index page: {url}")
            
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {url}, status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all blog posts on the page
                article_elements = soup.select('article.blog-item')
                
                if not article_elements:
                    logger.info(f"No more articles found on page {page+1}")
                    break
                
                # Extract article URLs
                for article in article_elements:
                    link_element = article.select_one('a.blog-title-link')
                    if link_element and link_element.get('href'):
                        full_url = self.base_url + link_element.get('href')
                        if full_url not in blog_urls:  # Avoid duplicates
                            blog_urls.append(full_url)
                
                # Find the next offset
                next_link = soup.select_one('a.older-posts')
                if next_link and 'href' in next_link.attrs:
                    href = next_link['href']
                    offset_match = re.search(r'offset=(\d+)', href)
                    if offset_match:
                        current_offset = offset_match.group(1)
                    else:
                        logger.warning("Could not find offset in 'older posts' link")
                        break
                else:
                    logger.info("No 'older posts' link found, reached the end of blog posts")
                    break
                
                # Sleep to avoid overwhelming the server
                time.sleep(random.uniform(1.0, 2.0))
                
            except Exception as e:
                logger.error(f"Error scraping page {url}: {str(e)}")
                break
        
        logger.info(f"Found {len(blog_urls)} unique blog posts.")
        return blog_urls
    
    def scrape_blog_post(self, url):
        """Scrapes content from a single blog post with optimized selectors."""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch article {url}, status code: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the blog post title
            title_element = soup.select_one('h1.entry-title')
            title = title_element.text.strip() if title_element else "Unknown Title"
            
            # Extract the publication date
            date_element = soup.select_one('time.entry-date')
            pub_date = date_element.text.strip() if date_element else "Unknown Date"
            
            # Extract the main content
            content_element = soup.select_one('div.entry-content')
            
            # Extract images for potential reference
            images = []
            if content_element:
                img_elements = content_element.select('img')
                for img in img_elements:
                    if 'src' in img.attrs:
                        img_src = img['src']
                        img_alt = img.get('alt', '')
                        images.append({
                            'src': img_src,
                            'alt': img_alt
                        })
            
            # Process the main content text
            content = ""
            if content_element:
                # Remove any script or style elements
                for script in content_element.find_all(['script', 'style']):
                    script.decompose()
                
                # Get text with proper spacing
                content = content_element.get_text(separator='\n').strip()
                
                # Clean up excessive whitespace
                content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Extract categories and tags if available
            categories = []
            cat_elements = soup.select('a[rel="category tag"]')
            for cat in cat_elements:
                categories.append(cat.text.strip())
            
            # Extract any structured data (if available)
            structured_data = {}
            metadata_elements = soup.select('meta[property^="og:"]')
            for meta in metadata_elements:
                if 'property' in meta.attrs and 'content' in meta.attrs:
                    prop = meta['property'].replace('og:', '')
                    structured_data[prop] = meta['content']
            
            # Sleep to avoid overwhelming the server
            time.sleep(random.uniform(0.5, 1.5))
            
            return {
                'url': url,
                'title': title,
                'publication_date': pub_date,
                'content': content,
                'categories': categories,
                'images': images,
                'metadata': structured_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return None
    
    def scrape_all_articles(self, cache_file="bike_fit_articles.json"):
        """Scrapes all blog posts and caches them to a file with error handling."""
        # Check if we have cached data
        if os.path.exists(cache_file):
            logger.info(f"Loading cached articles from {cache_file}")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.articles = json.load(f)
                    return self.articles
            except json.JSONDecodeError:
                logger.warning(f"Cache file {cache_file} is corrupted. Will scrape fresh data.")
            except Exception as e:
                logger.warning(f"Error loading cache file: {str(e)}. Will scrape fresh data.")
        
        # Get all blog URLs
        blog_urls = self.get_all_blog_urls(start_offset=1486856971000)  # Use the offset from your URL
        
        # Scrape each blog post with retry mechanism
        for i, url in enumerate(blog_urls):
            logger.info(f"Scraping article {i+1}/{len(blog_urls)}: {url}")
            
            # Try up to 3 times to scrape the article
            for attempt in range(3):
                article = self.scrape_blog_post(url)
                if article:
                    self.articles.append(article)
                    break
                else:
                    logger.warning(f"Attempt {attempt+1}/3 failed. Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Save progress every 5 articles
            if (i + 1) % 5 == 0:
                logger.info(f"Saving progress after {i+1} articles")
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        # Final save
        if self.articles:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Scraped {len(self.articles)} articles successfully.")
        return self.articles


class BikeFitKnowledgeBase:
    """Processes blog content into a searchable knowledge base."""
    
    def __init__(self, articles):
        self.articles = articles
        self.paragraphs = []
        self.sentences = []
        self.tfidf_model = None
        self.tfidf_matrix = None
        self.bert_tokenizer = None
        self.bert_model = None
        self.categories = set()
        self.embeddings_cache = {}  # For caching BERT embeddings
        
    def extract_categories(self):
        """Extracts all categories from articles for better filtering."""
        for article in self.articles:
            if 'categories' in article:
                for category in article['categories']:
                    self.categories.add(category)
        logger.info(f"Extracted {len(self.categories)} categories")
        return self.categories
    
    def process_articles(self):
        """Processes articles into paragraphs and sentences with improved handling."""
        for article in self.articles:
            title = article['title']
            content = article['content']
            url = article['url']
            categories = article.get('categories', [])
            
            # Add the title as a special paragraph (higher weight in search)
            self.paragraphs.append({
                'text': f"TITLE: {title}",
                'source_title': title,
                'source_url': url,
                'categories': categories,
                'is_title': True
            })
            
            # Split content into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # Add each paragraph to our collection
            for para in paragraphs:
                # Skip very short paragraphs as they're usually not helpful
                if len(para.split()) < 4:
                    continue
                    
                self.paragraphs.append({
                    'text': para,
                    'source_title': title,
                    'source_url': url,
                    'categories': categories,
                    'is_title': False
                })
            
            # Split content into sentences
            sentences = sent_tokenize(content)
            
            # Add each sentence to our collection
            for sentence in sentences:
                # Skip very short sentences
                if len(sentence.strip()) > 20:
                    self.sentences.append({
                        'text': sentence.strip(),
                        'source_title': title,
                        'source_url': url,
                        'categories': categories
                    })
        
        logger.info(f"Processed {len(self.articles)} articles into {len(self.paragraphs)} paragraphs and {len(self.sentences)} sentences.")
    
    def build_tfidf_model(self):
        """Builds a TF-IDF model for paragraph similarity with optimized parameters."""
        texts = [p['text'] for p in self.paragraphs]
        
        # Use more sophisticated TF-IDF parameters
        self.tfidf_model = TfidfVectorizer(
            stop_words='english',
            max_df=0.85,  # Ignore terms that appear in >85% of documents
            min_df=2,     # Ignore terms that appear in <2 documents
            ngram_range=(1, 3),  # Use unigrams, bigrams, and trigrams
            max_features=5000    # Limit features to prevent memory issues
        )
        
        self.tfidf_matrix = self.tfidf_model.fit_transform(texts)
        logger.info("TF-IDF model built successfully.")
    
    def load_bert_model(self):
        """Loads a BERT model for semantic search with better error handling."""
        try:
            # Load pre-trained model and tokenizer - small but effective model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            logger.info(f"Loading BERT model: {model_name}")
            self.bert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.bert_model = AutoModel.from_pretrained(model_name)
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.bert_model = self.bert_model.to('cuda')
                logger.info("BERT model loaded on GPU.")
            else:
                logger.info("BERT model loaded on CPU.")
                
        except Exception as e:
            logger.error(f"Error loading BERT model: {str(e)}")
            logger.warning("Falling back to TF-IDF only.")
    
    def get_bert_embedding(self, text, cache=True):
        """Gets BERT embeddings for a given text with caching."""
        if not self.bert_model or not self.bert_tokenizer:
            return None
        
        # Check cache first if enabled
        if cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        try:
            # Tokenize and get model outputs
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            inputs = self.bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Move inputs to GPU if available
            if device == 'cuda':
                inputs = {key: val.to(device) for key, val in inputs.items()}
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            
            # Mean pooling to get sentence embedding
            attention_mask = inputs['attention_mask']
            token_embeddings = outputs.last_hidden_state
            
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            embedding = (sum_embeddings / sum_mask).squeeze().cpu().numpy()
            
            # Cache the result if enabled
            if cache:
                self.embeddings_cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def precompute_bert_embeddings(self, batch_size=32):
        """Precomputes BERT embeddings for all paragraphs for faster search."""
        if not self.bert_model or not self.bert_tokenizer:
            logger.warning("BERT model not available, skipping embedding precomputation")
            return
        
        logger.info(f"Precomputing embeddings for {len(self.paragraphs)} paragraphs")
        
        for i in range(0, len(self.paragraphs), batch_size):
            batch = self.paragraphs[i:i+batch_size]
            for para in batch:
                text = para['text']
                self.get_bert_embedding(text, cache=True)
            
            if i % 100 == 0 and i > 0:
                logger.info(f"Precomputed embeddings for {i} paragraphs")
    
    def search_tfidf(self, query, top_n=5, category_filter=None):
        """Searches for relevant paragraphs using TF-IDF with category filtering."""
        query_vec = self.tfidf_model.transform([query])
        similarity = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get all indices in sorted order
        indices = similarity.argsort()[::-1]
        
        results = []
        for i in indices:
            # Skip if similarity is too low
            if similarity[i] < 0.1:
                continue
                
            # Apply category filter if specified
            if category_filter:
                if not set(category_filter).intersection(set(self.paragraphs[i].get('categories', []))):
                    continue
            
            # Add extra weight to title matches
            score = float(similarity[i])
            if self.paragraphs[i].get('is_title', False):
                score *= 1.5  # Boost title relevance
            
            results.append({
                'text': self.paragraphs[i]['text'].replace('TITLE: ', '') if self.paragraphs[i].get('is_title', False) else self.paragraphs[i]['text'],
                'score': score,
                'source_title': self.paragraphs[i]['source_title'],
                'source_url': self.paragraphs[i]['source_url'],
                'is_title': self.paragraphs[i].get('is_title', False)
            })
            
            if len(results) >= top_n:
                break
        
        return results
    
    def search_semantic(self, query, top_n=5, category_filter=None):
        """Searches for relevant paragraphs using semantic search with optimizations."""
        if not self.bert_model:
            return self.search_tfidf(query, top_n, category_filter)
        
        try:
            # Get query embedding
            query_embedding = self.get_bert_embedding(query)
            if query_embedding is None:
                logger.warning("Failed to generate query embedding, falling back to TF-IDF")
                return self.search_tfidf(query, top_n, category_filter)
            
            # Calculate similarities for all paragraphs
            similarities = []
            
            for i, para in enumerate(self.paragraphs):
                # Apply category filter if specified
                if category_filter and not set(category_filter).intersection(set(para.get('categories', []))):
                    continue
                
                # Get paragraph embedding (from cache if available)
                para_embedding = self.get_bert_embedding(para['text'])
                if para_embedding is None:
                    continue
                
                # Calculate cosine similarity
                similarity = cosine_similarity([query_embedding], [para_embedding])[0][0]
                
                # Apply boosting for titles
                if para.get('is_title', False):
                    similarity *= 1.5
                
                similarities.append((i, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top results
            results = []
            for i, score in similarities[:top_n]:
                if score > 0.5:  # Threshold for relevance
                    results.append({
                        'text': self.paragraphs[i]['text'].replace('TITLE: ', '') if self.paragraphs[i].get('is_title', False) else self.paragraphs[i]['text'],
                        'score': float(score),
                        'source_title': self.paragraphs[i]['source_title'],
                        'source_url': self.paragraphs[i]['source_url'],
                        'is_title': self.paragraphs[i].get('is_title', False)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error during semantic search: {str(e)}")
            logger.warning("Falling back to TF-IDF search")
            return self.search_tfidf(query, top_n, category_filter)


class BikeFitQAModel:
    """Model for answering bike fitting questions with improved answer generation."""
    
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.model_type = "retrieval"  
        self.category_mapping = {
            # Map common question topics to categories
            'saddle': ['Saddle', 'Comfort', 'Position'],
            'handlebar': ['Handlebars', 'Position', 'Comfort'],
            'cleat': ['Cleats', 'Pedals', 'Foot Position'],
            'knee': ['Knee Pain', 'Injuries', 'Position'],
            'pain': ['Injuries', 'Comfort'],
            'height': ['Bike Size', 'Position'],
            'size': ['Bike Size', 'Frame'],
            'fit': ['Bike Fit', 'Position']
        }
    
    def guess_categories(self, question):
        """Guess relevant categories based on the question keywords."""
        question_lower = question.lower()
        relevant_categories = set()
        
        for keyword, categories in self.category_mapping.items():
            if keyword in question_lower:
                relevant_categories.update(categories)
        
        return list(relevant_categories) if relevant_categories else None
    
    def generate_answer(self, search_results):
        """Generate a more coherent answer from multiple search results."""
        if not search_results:
            return "I don't have enough information to answer this question confidently."
        
        # If we only have one result or a very high scoring top result, just use it
        if len(search_results) == 1 or search_results[0]['score'] > 0.8:
            return search_results[0]['text']
        
        # Check if the top result is a title - if so, combine with the next best content
        if search_results[0].get('is_title', False) and len(search_results) > 1:
            return f"{search_results[0]['text']}\n\n{search_results[1]['text']}"
        
        # For multiple results, try to create a coherent answer
        # Start with the highest scoring result
        answer = search_results[0]['text']
        
        # Add other relevant information that doesn't repeat what's already included
        for i in range(1, min(3, len(search_results))):
            # Simple heuristic: if this paragraph adds substantial new content, include it
            current_result = search_results[i]['text']
            
            # Skip if too similar to content we already included
            if self.is_substantially_new(current_result, answer):
                answer += f"\n\n{current_result}"
        
        return answer
    
    def is_substantially_new(self, new_text, existing_text, threshold=0.5):
        """Check if new_text adds substantial new information compared to existing_text."""
        # Simple heuristic: check word overlap
        existing_words = set(existing_text.lower().split())
        new_words = set(new_text.lower().split())
        
        # Calculate Jaccard similarity
        intersection = existing_words.intersection(new_words)
        union = existing_words.union(new_words)
        
        similarity = len(intersection) / len(union) if union else 1.0
        
        return similarity < threshold  # Lower similarity means more new information
    
    def answer_question(self, question, use_semantic=True, top_n=3):
        """Answers a bike fitting question using the knowledge base with category guessing."""
        # Try to guess relevant categories from the question
        category_filter = self.guess_categories(question)
        
        # Search for relevant content
        if use_semantic and self.knowledge_base.bert_model:
            search_results = self.knowledge_base.search_semantic(question, top_n=top_n, category_filter=category_filter)
        else:
            search_results = self.knowledge_base.search_tfidf(question, top_n=top_n, category_filter=category_filter)
        
        # If no results with category filter, try without filter
        if not search_results and category_filter:
            logger.info(f"No results found with category filter {category_filter}, trying without filter")
            if use_semantic and self.knowledge_base.bert_model:
                search_results = self.knowledge_base.search_semantic(question, top_n=top_n)
            else:
                search_results = self.knowledge_base.search_tfidf(question, top_n=top_n)
        
        if not search_results:
            return {
                'answer': "I don't have enough information to answer this question confidently.",
                'sources': []
            }
        
        # Generate a more coherent answer
        answer = self.generate_answer(search_results)
        
        # Extract sources
        sources = []
        for result in search_results:
            if result['source_url'] not in [s['url'] for s in sources]:
                sources.append({
                    'title': result['source_title'],
                    'url': result['source_url'],
                    'relevance': result['score']
                })
        
        return {
            'answer': answer,
            'sources': sources
        }


class BikeFitQASystem:
    """Complete system for bike fitting QA with improved initialization and error handling."""
   
    
    def __init__(self, cache_file="bike_fit_articles.json"):
        self.cache_file = cache_file
        self.scraper = None
        self.knowledge_base = None
        self.qa_model = None
        self.is_initialized = False
        self.initialization_error = None
        
    def initialize(self, force_scrape=False, precompute_embeddings=True):
        """Initializes the entire system with robust error handling."""
        if self.is_initialized:
            return True
            
        try:
            logger.info("Initializing Bike Fit QA System")
            
            # Initialize scraper
            self.scraper = BikeFitScraper()
            
            # Check if cache exists and we don't want to force scrape
            articles = None
            if not force_scrape and os.path.exists(self.cache_file):
                logger.info(f"Attempting to load cached articles from {self.cache_file}")
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                    if not articles:  # Check if loaded data is empty
                        logger.warning("Cached file is empty, will scrape fresh data")
                        articles = None
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"Failed to load cache file {self.cache_file}: {str(e)}. Will scrape fresh data.")
                    articles = None
            
            # If no valid cached articles, scrape fresh data
            if articles is None:
                logger.info("Scraping fresh articles from Bike Fit Adviser")
                articles = self.scraper.scrape_all_articles(self.cache_file)
            
            # Validate articles
            if not articles or not isinstance(articles, list) or len(articles) == 0:
                self.initialization_error = "Failed to retrieve any valid articles after scraping."
                logger.error(self.initialization_error)
                return False
            
            # Initialize knowledge base
            logger.info(f"Building knowledge base from {len(articles)} articles")
            self.knowledge_base = BikeFitKnowledgeBase(articles)
            self.knowledge_base.process_articles()
            self.knowledge_base.extract_categories()
            self.knowledge_base.build_tfidf_model()
            
            # Try to load BERT model, but continue if it fails
            try:
                self.knowledge_base.load_bert_model()
                if precompute_embeddings:
                    self.knowledge_base.precompute_bert_embeddings()
            except Exception as e:
                logger.warning(f"BERT model could not be loaded. Using TF-IDF only. Error: {str(e)}")
            
            # Initialize QA model
            logger.info("Initializing QA model")
            self.qa_model = BikeFitQAModel(self.knowledge_base)
            
            self.is_initialized = True
            logger.info("Bike Fit QA System initialized successfully")
            return True
            
        except Exception as e:
            self.initialization_error = f"Error initializing system: {str(e)}"
            logger.error(self.initialization_error)
            return False
            
            # Initialize QA model
            logger.info("Initializing QA model")
            self.qa_model = BikeFitQAModel(self.knowledge_base)
            
            self.is_initialized = True
            logger.info("Bike Fit QA System initialized successfully")
            return True
            
        except Exception as e:
            self.initialization_error = f"Error initializing system: {str(e)}"
            logger.error(self.initialization_error)
            return False
    
    def answer_question(self, question, use_semantic=True):
        """Answers a bike fitting question with fallback options."""
        if not self.is_initialized:
            success = self.initialize()
            if not success:
                return {
                    'answer': f"The system is not properly initialized and cannot answer questions at this time. Error: {self.initialization_error}",
                    'sources': []
                }
        
        try:
            return self.qa_model.answer_question(question, use_semantic=use_semantic)
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            
            # Try with TF-IDF if semantic search fails
            if use_semantic:
                logger.info("Falling back to TF-IDF search")
                try:
                    return self.qa_model.answer_question(question, use_semantic=False)
                except Exception as e2:
                    logger.error(f"TF-IDF fallback also failed: {str(e2)}")
            
            return {
                'answer': "I encountered a technical issue while trying to answer your question. Please try again or rephrase your question.",
                'sources': []
            }
    
    def get_system_stats(self):
        """Returns system statistics for monitoring."""
        if not self.is_initialized:
            return {
                'status': 'Not initialized',
                'error': self.initialization_error
            }
        
        stats = {
            'status': 'Initialized',
            'articles_count': len(self.knowledge_base.articles),
            'paragraphs_count': len(self.knowledge_base.paragraphs),
            'sentences_count': len(self.knowledge_base.sentences),
            'categories': list(self.knowledge_base.categories),
            'bert_model_loaded': self.knowledge_base.bert_model is not None,
            'embeddings_cached': len(self.knowledge_base.embeddings_cache)
        }
        
        return stats


def test_bike_fit_qa_system():
    """Tests the bike fitting QA system with sample questions."""
    system = BikeFitQASystem()
    system.initialize()
    
    # Print system stats
    stats = system.get_system_stats()
    logger.info(f"System stats: {stats}")
    
    test_questions = [
        "How do I adjust saddle height?",
        "What causes knee pain in cycling?",
        "How should I position my cleats?",
        "What's the proper handlebar width for me?",
        "How do I know if my bike is too big?",
        "What should I do if my lower back hurts when cycling?",
        "How do I determine the right stem length?",
        "What's the best saddle angle for road cycling?",
        "How do I fix numbness in my hands while riding?",
        "What bike measurements are most important for a good fit?"
    ]
    
    for question in test_questions:
        logger.info(f"\nQuestion: {question}")
        response = system.answer_question(question, use_semantic=True)
        
        # Format and log the response
        logger.info(f"Answer: {response['answer']}")
        logger.info("Sources:")
        for source in response['sources']:
            logger.info(f"- {source['title']} ({source['url']}, relevance: {source['relevance']:.2f})")
        
        # Add a small delay between questions to simulate real usage
        time.sleep(0.5)

def main():
    """
    Main function to demonstrate integration and usage of the BikeFitQASystem.
    Can be imported and used in your application.
    """
    # Initialize the QA system once
    qa_system = BikeFitQASystem()
    
    # You can set force_scrape=True if you want fresh data each time
    if qa_system.initialize(force_scrape=False, precompute_embeddings=True):
        logger.info("System ready for questions")
    else:
        logger.error("System initialization failed")
        return
    
    # Example of how to integrate into your application
    def ask_question(question):
        """Helper function to integrate into your app"""
        response = qa_system.answer_question(question, use_semantic=True)
        return {
            'question': question,
            'answer': response['answer'],
            'sources': response['sources']
        }
    
    # Test with a few questions programmatically
    sample_questions = [
        "How do I adjust saddle height?",
        "What causes knee pain in cycling?"
    ]
    
    for q in sample_questions:
        result = ask_question(q)
        print(f"\nQ: {result['question']}")
        print(f"A: {result['answer']}")
        print("Sources:")
        for source in result['sources']:
            print(f"- {source['title']} ({source['url']})")
    
    # Optionally run the full test suite
    print("\nRunning full test suite...")
    test_bike_fit_qa_system()

if __name__ == "__main__":
    main()