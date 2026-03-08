from typing import Optional, Dict, Any, List
from openai import OpenAI
from anthropic import Anthropic
import httpx
import logging
from datetime import datetime
from sqlmodel import select

from app.core.config import settings
from app.db.models import LLMConfig, Card, CardType, Project
from app.schemas import AIGenerateRequest, AIGenerateResponse

logger = logging.getLogger(__name__)

class AIService:
    """AI服务基类"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._create_client()

    def _create_client(self):
        """根据提供商创建客户端"""
        if self.config.provider == "openai":
            return OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or settings.openai_base_url
            )
        elif self.config.provider == "anthropic":
            return Anthropic(
                api_key=self.config.api_key
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """通用生成方法"""
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, 
            max_tokens: int = 2000) -> str:
        """聊天生成方法"""
        raise NotImplementedError


class OpenAIService(AIService):
    """OpenAI服务实现"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """生成响应"""
        full_prompt = self._format_prompt(prompt, context)

        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的软件开发助手，能够帮助用户创建和管理卡片式开发流程。"
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content
            self._update_usage(response.usage)

            return content

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
            max_tokens: int = 2000) -> str:
        """聊天生成"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content
            self._update_usage(response.usage)

            return content

        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise

    def _format_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """格式化提示词"""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            return f"上下文信息：\n{context_str}\n\n用户请求：\n{prompt}"
        return prompt

    def _update_usage(self, usage):
        """更新使用统计"""
        # TODO: 更新数据库中的使用统计
        logger.debug(f"Usage: input={usage.prompt_tokens}, output={usage.completion_tokens}")


class AnthropicService(AIService):
    """Anthropic Claude服务实现"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """生成响应"""
        full_prompt = self._format_prompt(prompt, context)

        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system="你是一个专业的软件开发助手，能够帮助用户创建和管理卡片式开发流程。",
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )

            content = response.content[0].text
            self._update_usage(response.usage)

            return content

        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
            max_tokens: int = 2000) -> str:
        """聊天生成"""
        # Anthropic的chat方法直接使用messages参数
        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system="你是一个专业的软件开发助手。",
                messages=messages
            )

            content = response.content[0].text
            self._update_usage(response.usage)

            return content

        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise

    def _format_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """格式化提示词"""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            return f"上下文信息：\n{context_str}\n\n用户请求：\n{prompt}"
        return prompt

    def _update_usage(self, usage):
        """更新使用统计"""
        logger.debug(f"Usage: input={usage.input_tokens}, output={usage.output_tokens}")


class AIManager:
    """AI服务管理器"""

    def __init__(self, db_session):
        self.db = db_session
        self.services: Dict[str, AIService] = {}

    def _get_default_config(self) -> LLMConfig:
        """获取默认配置"""
        # 查询是否有可用的配置
        statement = select(LLMConfig).where(
            LLMConfig.api_key != None,
            LLMConfig.api_key != "",
            LLMConfig.model_name != None,
            LLMConfig.provider != None
        ).order_by(LLMConfig.created_at)

        configs = self.db.exec(statement).all()

        if not configs:
            raise ValueError("No LLM configuration found. Please configure AI models in settings.")

        return configs[0]

    def _get_config(self, config_id: Optional[int] = None) -> LLMConfig:
        """获取配置"""
        if config_id:
            config = self.db.get(LLMConfig, config_id)
            if not config:
                raise ValueError(f"LLM config with id {config_id} not found")
            return config
        return self._get_default_config()

    def get_service(self, config_id: Optional[int] = None) -> AIService:
        """获取AI服务实例"""
        config_id_str = str(config_id) if config_id else "default"

        if config_id_str not in self.services:
            config = self._get_config(config_id)
            if config.provider == "openai":
                self.services[config_id_str] = OpenAIService(config)
            elif config.provider == "anthropic":
                self.services[config_id_str] = AnthropicService(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

        return self.services[config_id_str]

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                temperature: float = 0.7, max_tokens: int = 2000,
                llm_config_id: Optional[int] = None) -> AIGenerateResponse:
        """生成内容"""
        service = self.get_service(llm_config_id)
        content = service.generate(prompt, context, temperature, max_tokens)

        # 返回响应
        return AIGenerateResponse(
            content=content,
            model=service.config.model_name,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            token_count=0
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
            max_tokens: int = 2000, llm_config_id: Optional[int] = None) -> str:
        """聊天生成"""
        service = self.get_service(llm_config_id)
        return service.chat(messages, temperature, max_tokens)

    async def async_generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                            temperature: float = 0.7, max_tokens: int = 2000,
                            llm_config_id: Optional[int] = None) -> str:
        """异步生成"""
        # 使用异步HTTP客户端
        async with httpx.AsyncClient() as client:
            config = self._get_config(llm_config_id)

            if config.provider == "openai":
                return await self._async_openai_generate(client, config, prompt, context, temperature, max_tokens)
            elif config.provider == "anthropic":
                return await self._async_anthropic_generate(client, config, prompt, context, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

    async def _async_openai_generate(self, client: httpx.AsyncClient, config: LLMConfig,
                                    prompt: str, context: Optional[Dict[str, Any]],
                                    temperature: float, max_tokens: int) -> str:
        """异步OpenAI生成"""
        url = f"{config.base_url or settings.openai_base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {config.api_key}"}
        payload = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业的软件开发助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            payload["messages"][1]["content"] = f"上下文信息：\n{context_str}\n\n用户请求：\n{prompt}"

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _async_anthropic_generate(self, client: httpx.AsyncClient, config: LLMConfig,
                                       prompt: str, context: Optional[Dict[str, Any]],
                                       temperature: float, max_tokens: int) -> str:
        """异步Anthropic生成"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])

        payload = {
            "model": config.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": "你是一个专业的软件开发助手。",
            "messages": [
                {"role": "user", "content": f"{context_str}\n\n用户请求：\n{prompt}"}
            ]
        }

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["content"][0]["text"]