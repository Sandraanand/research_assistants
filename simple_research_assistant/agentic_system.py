"""
TRUE AGENTIC AI VERSION
Using Autogen 0.4 - Proper agent framework with autonomy
"""
import asyncio
from typing import Dict, Any, List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.base import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from config import config
from pubmed_utils import search_pubmed


class AgenticResearchSystem:
    """
    TRUE AGENTIC AI SYSTEM
    - Autonomous agents with decision-making
    - Agent-to-agent communication
    - Self-directed workflow
    - Real Autogen framework
    """
    
    def __init__(self):
        """Initialize agentic system with autonomous agents"""
        print("🤖 Initializing AGENTIC AI system...")
        
        # Create model client for all agents
        self.model_client = AzureOpenAIChatCompletionClient(
            model=config.AZURE_OPENAI_DEPLOYMENT,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
        )
        
        # Create autonomous agents
        self.coordinator_agent = self._create_coordinator_agent()
        self.literature_agent = self._create_literature_agent()
        self.synthesis_agent = self._create_synthesis_agent()
        self.extension_agent = self._create_extension_agent()
        self.explainer_agent = self._create_explainer_agent()
        self.advisor_agent = self._create_advisor_agent()
        
        print("✅ Agentic AI system ready - 6 autonomous agents initialized")
    
    def _create_coordinator_agent(self) -> AssistantAgent:
        """Coordinator - Decides workflow and delegates tasks"""
        return AssistantAgent(
            name="Coordinator",
            model_client=self.model_client,
            system_message="""You are the Coordinator Agent in a multi-agent research system.

Your role:
- Analyze user requests
- Decide which agents to activate
- Coordinate agent communication
- Make autonomous decisions about workflow

Available agents:
1. Literature_Agent - Searches papers
2. Synthesis_Agent - Summarizes papers
3. Extension_Agent - Proposes future research
4. Explainer_Agent - Explains concepts
5. Advisor_Agent - Checks papers

When user provides a research topic:
1. Activate Literature_Agent for search
2. If papers found, activate Synthesis_Agent
3. Then activate Extension_Agent
4. Coordinate their outputs

When user asks to explain a concept:
- Directly activate Explainer_Agent

When user submits a paper:
- Directly activate Advisor_Agent

Make autonomous decisions. Communicate with other agents.""",
        )
    
    def _create_literature_agent(self) -> AssistantAgent:
        """Literature Agent - Autonomous paper search"""
        return AssistantAgent(
            name="Literature_Agent",
            model_client=self.model_client,
            system_message="""You are an autonomous Literature Search Agent.

Your capabilities:
- Search PubMed for relevant papers
- Evaluate paper relevance
- Extract key information
- Decide search strategy autonomously

When activated:
1. Analyze the research topic
2. Formulate optimal search query
3. Request paper search (use search_papers tool)
4. Filter and rank results
5. Report findings to Coordinator

Be proactive and thorough. Make your own decisions about search strategies.""",
            tools=[self._create_search_tool()],
        )
    
    def _create_synthesis_agent(self) -> AssistantAgent:
        """Synthesis Agent - Autonomous analysis"""
        return AssistantAgent(
            name="Synthesis_Agent",
            model_client=self.model_client,
            system_message="""You are an autonomous Reading Synthesis Agent.

Your capabilities:
- Analyze research papers independently
- Identify patterns and themes
- Extract key findings
- Make connections between papers

When activated with papers:
1. Read and analyze each paper
2. Identify main contributions
3. Extract methodologies
4. Find common themes
5. Synthesize into coherent summary

Be analytical and insightful. Work autonomously.""",
        )
    
    def _create_extension_agent(self) -> AssistantAgent:
        """Extension Agent - Autonomous research planning"""
        return AssistantAgent(
            name="Extension_Agent",
            model_client=self.model_client,
            system_message="""You are an autonomous Future Research Extension Agent.

Your capabilities:
- Identify research gaps independently
- Propose novel research directions
- Design solution approaches
- Assess feasibility autonomously

When activated with synthesis:
1. Analyze current research landscape
2. Identify gaps and opportunities
3. Propose 3-5 extensions
4. Provide implementation approaches
5. Assess difficulty and impact

Be innovative and strategic. Make autonomous proposals.""",
        )
    
    def _create_explainer_agent(self) -> AssistantAgent:
        """Explainer Agent - Autonomous teaching"""
        return AssistantAgent(
            name="Explainer_Agent",
            model_client=self.model_client,
            system_message="""You are an autonomous Concept Explanation Agent.

Your capabilities:
- Explain complex topics independently
- Choose appropriate analogies
- Create relevant examples
- Adapt explanation level

When activated with a concept:
1. Analyze the concept complexity
2. Determine explanation approach
3. Create simple definition
4. Generate relevant examples
5. Develop helpful analogies

Be clear and engaging. Work autonomously.""",
        )
    
    def _create_advisor_agent(self) -> AssistantAgent:
        """Advisor Agent - Autonomous review"""
        return AssistantAgent(
            name="Advisor_Agent",
            model_client=self.model_client,
            system_message="""You are an autonomous Paper Advisory Agent.

Your capabilities:
- Review papers independently
- Assess structure and format
- Provide constructive feedback
- Make submission recommendations

When activated with a paper:
1. Analyze paper structure
2. Check required sections
3. Evaluate formatting quality
4. Identify improvements
5. Provide actionable feedback

Be thorough and constructive. Work autonomously.""",
        )
    
    def _create_search_tool(self):
        """Create tool for Literature Agent to search papers"""
        async def search_papers(topic: str, max_results: int = 5) -> str:
            """Search PubMed for papers"""
            papers = search_pubmed(topic, max_results)
            if not papers:
                return "No papers found"
            
            result = []
            for i, paper in enumerate(papers, 1):
                result.append(
                    f"Paper {i}: {paper['title']}\n"
                    f"Authors: {', '.join(paper['authors'][:3])}\n"
                    f"Abstract: {paper.get('abstract', 'N/A')[:200]}...\n"
                    f"Link: {paper['link']}\n"
                )
            return "\n".join(result)
        
        return search_papers
    
    async def run_agentic_workflow(
        self,
        user_request: str,
        task_type: str = "research"  # research, explain, review
    ) -> Dict[str, Any]:
        """
        Run AGENTIC workflow - Agents communicate autonomously
        
        Args:
            user_request: User's request
            task_type: Type of task (research, explain, review)
            
        Returns:
            Results from agent collaboration
        """
        print(f"\n🤖 Starting AGENTIC workflow: {task_type}")
        print(f"📝 Request: {user_request}\n")
        
        # Select agents based on task type
        if task_type == "research":
            agents = [
                self.coordinator_agent,
                self.literature_agent,
                self.synthesis_agent,
                self.extension_agent
            ]
            max_turns = 10
        
        elif task_type == "explain":
            agents = [
                self.coordinator_agent,
                self.explainer_agent
            ]
            max_turns = 3
        
        elif task_type == "review":
            agents = [
                self.coordinator_agent,
                self.advisor_agent
            ]
            max_turns = 3
        
        else:
            agents = [self.coordinator_agent]
            max_turns = 5
        
        # Create agentic team with RoundRobin (agents take turns autonomously)
        team = RoundRobinGroupChat(
            participants=agents,
            max_turns=max_turns
        )
        
        # Run agentic conversation
        print("🔄 Agents are now communicating autonomously...\n")
        
        try:
            # Create cancellation token
            cancellation_token = CancellationToken()
            
            # Run the team
            result = await team.run(
                task=user_request,
                cancellation_token=cancellation_token
            )
            
            # Extract messages from agent conversation
            messages = []
            async for message in result.messages:
                agent_name = message.source if hasattr(message, 'source') else "Unknown"
                content = message.content if hasattr(message, 'content') else str(message)
                messages.append({
                    "agent": agent_name,
                    "message": content
                })
                print(f"🤖 {agent_name}: {content[:100]}...")
            
            print("\n✅ Agentic workflow completed!\n")
            
            return {
                "task_type": task_type,
                "request": user_request,
                "messages": messages,
                "final_result": messages[-1]["message"] if messages else "No result",
                "is_agentic": True,
                "agents_used": [agent.name for agent in agents]
            }
        
        except Exception as e:
            print(f"❌ Agentic workflow error: {e}")
            return {
                "task_type": task_type,
                "error": str(e),
                "is_agentic": True
            }
    
    async def explain_concept_agentic(self, concept: str, context: str = None) -> str:
        """
        Explain concept using AGENTIC approach
        Explainer agent works autonomously
        """
        request = f"Explain the concept '{concept}' in simple terms."
        if context:
            request += f" Context: {context}"
        
        result = await self.run_agentic_workflow(
            user_request=request,
            task_type="explain"
        )
        
        return result.get("final_result", "")
    
    async def review_paper_agentic(self, title: str, content: str) -> Dict[str, Any]:
        """
        Review paper using AGENTIC approach
        Advisor agent works autonomously
        """
        request = f"""Review this paper for submission:

Title: {title}

Content (preview):
{content[:1000]}

Provide:
1. Structure assessment
2. Missing sections
3. Formatting score (0-100)
4. Recommendations"""
        
        result = await self.run_agentic_workflow(
            user_request=request,
            task_type="review"
        )
        
        return {
            "feedback": result.get("final_result", ""),
            "is_agentic": True,
            "agent_used": "Advisor_Agent"
        }


# Global instance
_agentic_system = None


def get_agentic_system() -> AgenticResearchSystem:
    """Get or create agentic system"""
    global _agentic_system
    if _agentic_system is None:
        _agentic_system = AgenticResearchSystem()
    return _agentic_system


# Example usage
async def example_agentic_research():
    """Example: How agentic AI works"""
    
    system = get_agentic_system()
    
    # Agentic research workflow
    result = await system.run_agentic_workflow(
        user_request="Find recent papers on deep learning in medical imaging and propose future research directions",
        task_type="research"
    )
    
    print("\n📊 AGENTIC RESULT:")
    print(f"Agents used: {result['agents_used']}")
    print(f"Agent messages: {len(result['messages'])}")
    print(f"Is agentic: {result['is_agentic']}")


if __name__ == "__main__":
    asyncio.run(example_agentic_research())
