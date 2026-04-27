"""
LLM service using OpenAI GPT-4 with streaming support
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, AsyncGenerator, Optional
import logging
from models.conversation import Message, MessageRole, ToolCall
from config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """GPT-4 service with streaming and tool use"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    async def generate_response(
        self,
        messages: List[Message],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a response from GPT-4
        
        Args:
            messages: Conversation history
            system_prompt: System prompt for the agent
            tools: Optional tool definitions for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages(messages, system_prompt)
            
            # Prepare request parameters
            request_params = {
                "model": self.settings.openai_model,
                "messages": openai_messages,
                "temperature": temperature or self.settings.openai_temperature,
                "max_tokens": max_tokens
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract response
            message = response.choices[0].message
            
            # Check for tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Tool calls requested: {len(message.tool_calls)}")
                # Return tool call information
                return self._format_tool_calls(message.tool_calls)
            
            content = message.content or ""
            logger.info(f"Generated response: {content[:100]}...")
            
            return content
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        messages: List[Message],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from GPT-4
        
        Yields tokens as they are generated for real-time responses.
        """
        try:
            # Convert messages
            openai_messages = self._convert_messages(messages, system_prompt)
            
            # Prepare request
            request_params = {
                "model": self.settings.openai_model,
                "messages": openai_messages,
                "temperature": temperature or self.settings.openai_temperature,
                "stream": True
            }
            
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Stream response
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield token
                    
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
    
    def _convert_messages(
        self,
        messages: List[Message],
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """Convert internal messages to OpenAI format"""
        openai_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            # Handle both enum and string values
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            openai_messages.append({
                "role": role,
                "content": msg.content
            })
        
        return openai_messages
    
    def _format_tool_calls(self, tool_calls) -> str:
        """Format tool calls for processing"""
        # This is a simplified version
        # In production, you'd return structured data
        calls = []
        for call in tool_calls:
            calls.append(f"TOOL_CALL: {call.function.name}({call.function.arguments})")
        return "\n".join(calls)
    
    async def analyze_intent(
        self,
        user_message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze user intent for routing
        
        Returns:
            Dict with intent, confidence, and suggested agent
        """
        try:
            prompt = f"""Analyze the user's intent and determine the best agent to handle this request.

User message: "{user_message}"
{f'Context: {context}' if context else ''}

Available agents:
- support: Technical issues, complaints, product questions
- booking: Appointments, scheduling, calendar
- general: Casual conversation, general information
- analytics: Metrics, insights, performance

Respond in JSON format:
{{
    "intent": "brief description",
    "agent": "agent_name",
    "confidence": 0.0-1.0,
    "reasoning": "why this agent"
}}"""

            messages = [Message(role=MessageRole.USER, content=prompt)]
            response = await self.generate_response(
                messages=messages,
                system_prompt="You are an intent classification system. Always respond with valid JSON.",
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse JSON response
            import json
            import re
            
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                # Extract JSON from markdown code block
                match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
                if match:
                    response = match.group(1).strip()
            
            result = json.loads(response)
            return result
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            # Default to general agent
            return {
                "intent": "general_conversation",
                "agent": "general",
                "confidence": 0.5,
                "reasoning": "Error in intent detection, defaulting to general"
            }
    
    async def summarize_conversation(
        self,
        messages: List[Message],
        max_length: int = 200
    ) -> str:
        """Generate a concise conversation summary"""
        try:
            # Get last N messages
            recent_messages = messages[-10:]
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}"
                for msg in recent_messages
            ])
            
            prompt = f"""Summarize this conversation in {max_length} characters or less:

{conversation_text}

Summary:"""

            summary_messages = [Message(role=MessageRole.USER, content=prompt)]
            summary = await self.generate_response(
                messages=summary_messages,
                system_prompt="You are a conversation summarizer. Be concise and capture key points.",
                temperature=0.3,
                max_tokens=100
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return "Conversation in progress"
