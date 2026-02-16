"""
Research Orchestrator with Autogen 0.4 RoundRobin GroupChat
- Uses RoundRobinGroupChat for agent coordination
- Independent operations (no workflow required)
- Working agents with proper async handling
"""
from typing import Dict, Any, List, Optional, Callable
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models import AzureOpenAIChatCompletionClient
from autogen_core.components.models import UserMessage

from config import config
from pubmed_utils import search_pubmed


class ResearchOrchestrator:
    """
    Autogen 0.4 Research Orchestrator with RoundRobin GroupChat
    - Each function works independently
    - Agents coordinate via RoundRobin pattern
    - Direct API calls where possible for speed
    """
    
    def __init__(self):
        """Initialize orchestrator with Autogen 0.4 agents"""
        print("🤖 Initializing Autogen 0.4 Research Orchestrator...")
        
        # Create Azure OpenAI client
        self.model_client = AzureOpenAIChatCompletionClient(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            model=config.AZURE_OPENAI_DEPLOYMENT,
            model_capabilities={
                "vision": False,
                "function_calling": True,
                "json_output": True,
            }
        )
        
        # Create agents
        self._create_agents()
        
        print("✅ Autogen 0.4 Orchestrator initialized with RoundRobin GroupChat")
    
    def _create_agents(self):
        """Create all Autogen 0.4 agents"""
        
        # Literature Agent - Searches and retrieves papers
        self.literature_agent = AssistantAgent(
            name="LiteratureAgent",
            model_client=self.model_client,
            system_message="""You are a Literature Search Agent.
Your role: Search PubMed for research papers and format the results.

When given a topic:
1. Acknowledge the search request
2. Format the papers clearly with titles, authors, journals, dates, and links
3. Provide a count of papers found
4. End your message with: LITERATURE_COMPLETE

Be concise and structured."""
        )
        
        # Synthesis Agent - Summarizes papers
        self.synthesis_agent = AssistantAgent(
            name="SynthesisAgent",
            model_client=self.model_client,
            system_message="""You are a Paper Synthesis Agent.
Your role: Summarize research papers concisely.

For each paper:
- Main finding (1 sentence)
- Method used (1 sentence)
- Significance (1 sentence)

Format: Paper 1: [summary], Paper 2: [summary], ...
End your message with: SYNTHESIS_COMPLETE

Be clear and concise."""
        )
        
        # Extensions Agent - Proposes future research
        self.extensions_agent = AssistantAgent(
            name="ExtensionsAgent",
            model_client=self.model_client,
            system_message="""You are a Research Extensions Agent.
Your role: Propose future research directions based on current papers.

Generate 3 future research directions:
1. Title (brief)
2. Description (2 sentences)
3. Solution approach (1 sentence)
4. Difficulty (Easy/Medium/Hard)

Format clearly with numbers.
End your message with: EXTENSIONS_COMPLETE

Be innovative and specific."""
        )
        
        # Explainer Agent - Explains concepts
        self.explainer_agent = AssistantAgent(
            name="ExplainerAgent",
            model_client=self.model_client,
            system_message="""You are a Concept Explainer Agent.
Your role: Explain complex concepts in simple terms.

Include:
1. Simple definition (2 sentences)
2. Two concrete examples
3. One analogy
4. Why it matters

Max 200 words. Be clear and accessible.
End your message with: EXPLANATION_COMPLETE"""
        )
        
        # Advisor Agent - Checks paper formatting
        self.advisor_agent = AssistantAgent(
            name="AdvisorAgent",
            model_client=self.model_client,
            system_message="""You are a Paper Formatting Advisor Agent.
Your role: Review research papers for proper formatting.

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
- 3 quick recommendations

End your message with: ADVISOR_COMPLETE"""
        )
    
    async def search_literature(
        self, 
        topic: str, 
        max_papers: int = 5,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Search for literature using LiteratureAgent
        Direct PubMed API call for speed + agent formatting
        
        Args:
            topic: Research topic
            max_papers: Max papers to retrieve
            progress_callback: Optional progress callback
            
        Returns:
            Literature results
        """
        print(f"🔍 [LiteratureAgent] Searching PubMed for: {topic}")
        
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
        
        if progress_callback:
            progress_callback("Formatting results", 30)
        
        # Format papers with LiteratureAgent
        papers_text = self._format_papers_for_agent(papers)
        
        # Use agent to format output
        try:
            # Create single-agent "team" for independent operation
            termination = TextMentionTermination("LITERATURE_COMPLETE") | MaxMessageTermination(3)
            
            team = RoundRobinGroupChat(
                [self.literature_agent],
                termination_condition=termination
            )
            
            # Run agent
            message = f"""Format these {len(papers)} research papers clearly:

{papers_text}

Provide a structured list with all details."""
            
            result = await team.run(task=UserMessage(content=message, source="user"))
            
            # Extract formatted output
            formatted = self._extract_agent_response(result)
            
        except Exception as e:
            print(f"⚠️ Agent formatting failed, using fallback: {e}")
            formatted = self._format_papers(papers)
        
        if progress_callback:
            progress_callback("Papers retrieved", 40)
        
        print(f"✅ [LiteratureAgent] Found {len(papers)} papers")
        
        return {
            "papers": papers,
            "formatted": formatted,
            "count": len(papers)
        }
    
    async def synthesize_papers(
        self,
        papers: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Synthesize papers using SynthesisAgent
        
        Args:
            papers: List of papers to synthesize
            progress_callback: Optional progress callback
            
        Returns:
            Synthesis results
        """
        if not papers:
            return {"synthesis": "No papers to synthesize", "summaries": []}
        
        print(f"📖 [SynthesisAgent] Synthesizing {len(papers)} papers...")
        
        if progress_callback:
            progress_callback("Synthesizing papers", 60)
        
        try:
            # Create papers text
            papers_text = "\n\n".join([
                f"Paper {i}: {p['title']}\nAbstract: {p.get('abstract', 'N/A')[:300]}"
                for i, p in enumerate(papers, 1)
            ])
            
            # Use SynthesisAgent
            termination = TextMentionTermination("SYNTHESIS_COMPLETE") | MaxMessageTermination(3)
            
            team = RoundRobinGroupChat(
                [self.synthesis_agent],
                termination_condition=termination
            )
            
            message = f"""Summarize these {len(papers)} research papers:

{papers_text}

Provide concise summaries for each paper."""
            
            result = await team.run(task=UserMessage(content=message, source="user"))
            
            synthesis = self._extract_agent_response(result)
            
            if progress_callback:
                progress_callback("Synthesis complete", 80)
            
            print("✅ [SynthesisAgent] Synthesis complete")
            
            return {
                "synthesis": synthesis,
                "summaries": [{"paper": i, "summary": synthesis} for i in range(len(papers))]
            }
        
        except Exception as e:
            print(f"❌ [SynthesisAgent] Error: {e}")
            return {
                "synthesis": f"Error during synthesis: {str(e)}",
                "summaries": []
            }
    
    async def generate_extensions(
        self,
        papers_or_synthesis: Any,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate research extensions using ExtensionsAgent
        
        Args:
            papers_or_synthesis: Papers or synthesis results
            progress_callback: Optional progress callback
            
        Returns:
            Research extensions
        """
        print("🔮 [ExtensionsAgent] Generating research extensions...")
        
        if progress_callback:
            progress_callback("Generating research extensions", 90)
        
        try:
            # Extract context
            if isinstance(papers_or_synthesis, dict):
                context = papers_or_synthesis.get('synthesis', '')
            elif isinstance(papers_or_synthesis, str):
                context = papers_or_synthesis
            else:
                context = str(papers_or_synthesis)
            
            # Use ExtensionsAgent
            termination = TextMentionTermination("EXTENSIONS_COMPLETE") | MaxMessageTermination(3)
            
            team = RoundRobinGroupChat(
                [self.extensions_agent],
                termination_condition=termination
            )
            
            message = f"""Based on this research:

{context[:1000]}

Generate 3 innovative future research directions."""
            
            result = await team.run(task=UserMessage(content=message, source="user"))
            
            extensions = self._extract_agent_response(result)
            
            if progress_callback:
                progress_callback("Extensions generated", 100)
            
            print("✅ [ExtensionsAgent] Extensions generated")
            
            return {
                "extensions": extensions,
                "count": 3
            }
        
        except Exception as e:
            print(f"❌ [ExtensionsAgent] Error: {e}")
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
        Explain a concept using ExplainerAgent
        INDEPENDENT (no workflow needed)
        
        Args:
            concept: Concept to explain
            context: Optional context
            
        Returns:
            Simple explanation
        """
        print(f"💡 [ExplainerAgent] Explaining: {concept}")
        
        try:
            # Use ExplainerAgent
            termination = TextMentionTermination("EXPLANATION_COMPLETE") | MaxMessageTermination(3)
            
            team = RoundRobinGroupChat(
                [self.explainer_agent],
                termination_condition=termination
            )
            
            message = f"""Explain the concept '{concept}' in simple terms."""
            
            if context:
                message += f"\n\nContext: {context[:200]}"
            
            result = await team.run(task=UserMessage(content=message, source="user"))
            
            explanation = self._extract_agent_response(result)
            
            print("✅ [ExplainerAgent] Explanation generated")
            
            return explanation
        
        except Exception as e:
            print(f"❌ [ExplainerAgent] Error: {e}")
            return f"Error explaining concept: {str(e)}"
    
    async def check_paper(
        self,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Check paper formatting using AdvisorAgent
        INDEPENDENT (no workflow needed)
        
        Args:
            title: Paper title
            content: Paper content
            
        Returns:
            Formatting feedback
        """
        print(f"📝 [AdvisorAgent] Checking paper: {title}")
        
        try:
            # Only check first 1500 chars for speed
            content_preview = content[:1500]
            
            # Use AdvisorAgent
            termination = TextMentionTermination("ADVISOR_COMPLETE") | MaxMessageTermination(3)
            
            team = RoundRobinGroupChat(
                [self.advisor_agent],
                termination_condition=termination
            )
            
            message = f"""Review this research paper for formatting:

Title: {title}

Content (preview):
{content_preview}

Check for all required sections and provide feedback."""
            
            result = await team.run(task=UserMessage(content=message, source="user"))
            
            feedback = self._extract_agent_response(result)
            
            print("✅ [AdvisorAgent] Paper checked")
            
            return {"feedback": feedback}
        
        except Exception as e:
            print(f"❌ [AdvisorAgent] Error: {e}")
            return {"feedback": f"Error checking paper: {str(e)}"}
    
    async def run_full_workflow(
        self,
        topic: str,
        max_papers: int = 5,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run complete workflow using RoundRobinGroupChat
        ALL STEPS with agent coordination
        
        Args:
            topic: Research topic
            max_papers: Max papers
            progress_callback: Progress callback
            
        Returns:
            Complete results
        """
        print(f"\n🔬 [RoundRobin] Starting full research workflow: {topic}\n")
        
        # Step 1: Literature (LiteratureAgent)
        lit_result = await self.search_literature(topic, max_papers, progress_callback)
        
        if lit_result['count'] == 0:
            return {
                "topic": topic,
                "literature": "No papers found",
                "synthesis": "Cannot synthesize - no papers",
                "extensions": "Cannot generate extensions - no papers",
                "status": "completed_with_no_results"
            }
        
        # Step 2: Synthesis (SynthesisAgent)
        syn_result = await self.synthesize_papers(lit_result['papers'], progress_callback)
        
        # Step 3: Extensions (ExtensionsAgent)
        ext_result = await self.generate_extensions(syn_result, progress_callback)
        
        if progress_callback:
            progress_callback("Workflow completed", 100)
        
        print("\n✅ [RoundRobin] Full workflow completed!\n")
        
        return {
            "topic": topic,
            "literature": lit_result['formatted'],
            "synthesis": syn_result['synthesis'],
            "extensions": ext_result['extensions'],
            "status": "completed"
        }
    
    def _format_papers(self, papers: List[Dict]) -> str:
        """Format papers for display (fallback)"""
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
    
    def _format_papers_for_agent(self, papers: List[Dict]) -> str:
        """Format papers for agent processing"""
        result = []
        for i, paper in enumerate(papers, 1):
            result.append(f"""Paper {i}:
Title: {paper['title']}
Authors: {', '.join(paper['authors'][:3])}
Journal: {paper['journal']}
Date: {paper['pubdate']}
Link: {paper['link']}
DOI: {paper['doi']}
Abstract: {paper.get('abstract', 'N/A')[:200]}
""")
        return "\n\n".join(result)
    
    def _extract_agent_response(self, result) -> str:
        """Extract text response from agent result"""
        try:
            # Get last message from agent
            if hasattr(result, 'messages') and result.messages:
                last_message = result.messages[-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
            
            # Fallback
            return str(result)
        except Exception as e:
            print(f"⚠️ Error extracting response: {e}")
            return str(result)


# Global instance
_orchestrator = None


def get_orchestrator() -> ResearchOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResearchOrchestrator()
    return _orchestrator
