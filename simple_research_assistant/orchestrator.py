"""
Research Orchestrator - FIXED VERSION
- Proper async handling
- Independent operations (no workflow required)
- Working agents
- Fast and reliable
"""
from typing import Dict, Any, List, Optional
import asyncio
from config import config
from pubmed_utils import search_pubmed


class ResearchOrchestrator:
    """
    FIXED Research Orchestrator
    - Each function works independently
    - No complex async issues
    - Direct API calls where possible
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        print("✅ Research Orchestrator initialized")
    
    async def search_literature(
        self, 
        topic: str, 
        max_papers: int = 5,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Search for literature - WORKING VERSION
        Direct PubMed API call (no agents, no async issues)
        
        Args:
            topic: Research topic
            max_papers: Max papers to retrieve
            progress_callback: Optional progress callback
            
        Returns:
            Literature results
        """
        print(f"🔍 Searching PubMed for: {topic}")
        
        if progress_callback:
            progress_callback("Searching for papers", 20)
        
        # Direct PubMed search (fast, reliable)
        papers = search_pubmed(topic, max_papers)
        
        if not papers:
            return {
                "papers": [],
                "formatted": "No papers found for this topic.",
                "count": 0
            }
        
        # Format for display
        formatted = self._format_papers(papers)
        
        if progress_callback:
            progress_callback("Papers retrieved", 40)
        
        print(f"✅ Found {len(papers)} papers")
        
        return {
            "papers": papers,
            "formatted": formatted,
            "count": len(papers)
        }
    
    async def synthesize_papers(
        self,
        papers: List[Dict],
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Synthesize papers - Simple LLM call
        
        Args:
            papers: List of papers to synthesize
            progress_callback: Optional progress callback
            
        Returns:
            Synthesis results
        """
        if not papers:
            return {"synthesis": "No papers to synthesize", "summaries": []}
        
        print(f"📖 Synthesizing {len(papers)} papers...")
        
        if progress_callback:
            progress_callback("Synthesizing papers", 60)
        
        # Use simple OpenAI call instead of Autogen (more reliable)
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            
            # Create synthesis prompt
            papers_text = "\n\n".join([
                f"Paper {i}: {p['title']}\nAbstract: {p.get('abstract', 'N/A')[:300]}"
                for i, p in enumerate(papers, 1)
            ])
            
            prompt = f"""Summarize these {len(papers)} research papers concisely.

{papers_text}

For each paper, provide:
- Main finding (1 sentence)
- Method used (1 sentence)
- Significance (1 sentence)

Format: Paper 1: [summary], Paper 2: [summary], ..."""
            
            response = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a research paper summarizer. Be concise."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            synthesis = response.choices[0].message.content
            
            if progress_callback:
                progress_callback("Synthesis complete", 80)
            
            print("✅ Synthesis complete")
            
            return {
                "synthesis": synthesis,
                "summaries": [{"paper": i, "summary": synthesis} for i in range(len(papers))]
            }
        
        except Exception as e:
            print(f"❌ Synthesis error: {e}")
            return {
                "synthesis": f"Error during synthesis: {str(e)}",
                "summaries": []
            }
    
    async def generate_extensions(
        self,
        papers_or_synthesis: Any,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Generate research extensions - Simple LLM call
        
        Args:
            papers_or_synthesis: Papers or synthesis results
            progress_callback: Optional progress callback
            
        Returns:
            Research extensions
        """
        print("🔮 Generating research extensions...")
        
        if progress_callback:
            progress_callback("Generating research extensions", 90)
        
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            
            # Extract context
            if isinstance(papers_or_synthesis, dict):
                context = papers_or_synthesis.get('synthesis', '')
            elif isinstance(papers_or_synthesis, str):
                context = papers_or_synthesis
            else:
                context = str(papers_or_synthesis)
            
            prompt = f"""Based on this research summary:

{context[:1000]}

Generate 3 future research directions. For each provide:
1. Title (brief)
2. Description (2 sentences)
3. Solution approach (1 sentence)
4. Difficulty (Easy/Medium/Hard)

Format clearly with numbers."""
            
            response = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a research strategist. Propose innovative extensions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            extensions = response.choices[0].message.content
            
            if progress_callback:
                progress_callback("Extensions generated", 100)
            
            print("✅ Extensions generated")
            
            return {
                "extensions": extensions,
                "count": 3
            }
        
        except Exception as e:
            print(f"❌ Extensions error: {e}")
            return {
                "extensions": f"Error generating extensions: {str(e)}",
                "count": 0
            }
    
    async def explain_concept(
        self,
        concept: str,
        context: Optional[str] = None
    ) -> str:
        """
        Explain a concept - INDEPENDENT (no workflow needed)
        
        Args:
            concept: Concept to explain
            context: Optional context
            
        Returns:
            Simple explanation
        """
        print(f"💡 Explaining: {concept}")
        
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            
            prompt = f"""Explain the concept '{concept}' in simple terms.

Include:
1. Simple definition (2 sentences)
2. Two concrete examples
3. One analogy
4. Why it matters

Max 200 words. Be clear and accessible."""
            
            if context:
                prompt += f"\n\nContext: {context[:200]}"
            
            response = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a concept explainer. Use simple language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            explanation = response.choices[0].message.content
            
            print("✅ Explanation generated")
            
            return explanation
        
        except Exception as e:
            print(f"❌ Explanation error: {e}")
            return f"Error explaining concept: {str(e)}"
    
    async def check_paper(
        self,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Check paper formatting - INDEPENDENT (no workflow needed)
        
        Args:
            title: Paper title
            content: Paper content
            
        Returns:
            Formatting feedback
        """
        print(f"📝 Checking paper: {title}")
        
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            
            # Only check first 1500 chars for speed
            content_preview = content[:1500]
            
            prompt = f"""Review this research paper for formatting:

Title: {title}

Content (preview):
{content_preview}

Check for:
1. Abstract (present/missing)
2. Introduction (present/missing)
3. Methods (present/missing)
4. Results (present/missing)
5. Conclusion (present/missing)
6. References (present/missing)

Provide:
- Score (0-100)
- Missing sections
- 3 quick recommendations"""
            
            response = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a paper formatting checker. Be specific."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            feedback = response.choices[0].message.content
            
            print("✅ Paper checked")
            
            return {"feedback": feedback}
        
        except Exception as e:
            print(f"❌ Paper check error: {e}")
            return {"feedback": f"Error checking paper: {str(e)}"}
    
    async def run_full_workflow(
        self,
        topic: str,
        max_papers: int = 5,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Run complete workflow - ALL STEPS
        
        Args:
            topic: Research topic
            max_papers: Max papers
            progress_callback: Progress callback
            
        Returns:
            Complete results
        """
        print(f"\n🔬 Starting full research workflow: {topic}\n")
        
        # Step 1: Literature
        lit_result = await self.search_literature(topic, max_papers, progress_callback)
        
        if lit_result['count'] == 0:
            return {
                "topic": topic,
                "literature": "No papers found",
                "synthesis": "Cannot synthesize - no papers",
                "extensions": "Cannot generate extensions - no papers",
                "status": "completed_with_no_results"
            }
        
        # Step 2: Synthesis
        syn_result = await self.synthesize_papers(lit_result['papers'], progress_callback)
        
        # Step 3: Extensions
        ext_result = await self.generate_extensions(syn_result, progress_callback)
        
        if progress_callback:
            progress_callback("Workflow completed", 100)
        
        print("\n✅ Full workflow completed!\n")
        
        return {
            "topic": topic,
            "literature": lit_result['formatted'],
            "synthesis": syn_result['synthesis'],
            "extensions": ext_result['extensions'],
            "status": "completed"
        }
    
    def _format_papers(self, papers: List[Dict]) -> str:
        """Format papers for display"""
        result = []
        for i, paper in enumerate(papers, 1):
            result.append(f"""
**Paper {i}: {paper['title']}**
- Authors: {', '.join(paper['authors'][:3])}
- Journal: {paper['journal']}
- Date: {paper['pubdate']}
- Link: {paper['link']}
- DOI: {paper['doi']}
""")
        
        return "\n".join(result)


# Global instance
_orchestrator = None


def get_orchestrator() -> ResearchOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResearchOrchestrator()
    return _orchestrator
