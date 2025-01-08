from typing import List, Type, TypeVar, Generic, Tuple
import openai
import json
from pydantic import BaseModel

# Define a type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

class AzureOpenAiClient:
    def __init__(
        self,
        open_ai_key: str,
        base_endpoint: str,
        api_version: str ="2023-03-15-preview"
        ):
        """
        Initialize the AzureOpenAi with the OpenAI API key and endpoint.

        Args:
            open_ai_key (string): The API key for Azure OpenAI.
            base_endpoint (string): The base endpoint URL for Azure OpenAI.
            api_version (string): The API version to use (default is "2023-03-15-preview").
        """
        self.open_ai_key = open_ai_key
        self.base_endpoint = base_endpoint
        self.api_version = api_version
        self.open_ai_client = openai.AzureOpenAI(
            api_key=open_ai_key,
            api_version=api_version,
            azure_endpoint=base_endpoint
            )

    def chat_completions(
        self,
        model: str,
        system_content: str,
        user_content: str,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        **kwargs
        ) -> dict:
        """
        Send a chat completion request to the OpenAI API.

        Args:
            model (string): The model to use for the completion.
            system_content (string): The content for the system role.
            user_content (string): The content for the user role.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens to generate.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty parameter.
            presence_penalty (float): Presence penalty parameter.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            dict: The response from the OpenAI API.
        """
        message = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        response = self.open_ai_client.chat.completions.create(
            model=model,
            messages=message,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            **kwargs
        )

        return response

    def structured_chat_completion(
        self,
        model: str,
        system_content: str,
        user_content: str,
        response_format: Type[T],
        **kwargs
    ) -> T:
        """
        Send a chat completion request with structured output parsing. Pydantic models are needed to structure the output

        Args:
            model (string): The model to use for the completion.
            system_content (string): The content for the system role.
            user_content (string): The content for the user role.
            response_format (Type[T]): The Pydantic model to parse the response into.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            T: The parsed response as an instance of the provided Pydantic model.
        """
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        response = self.open_ai_client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_format,
            **kwargs
        )

        # Extract and parse the structured response
        parsed_response = response.choices[0].message.parsed

        return parsed_response

    def create_embedding(
        self,
        data_to_vectorize: str,
        embedding_model: str = "text-embedding-ada-002",
        embedding_dimensions: int = 1536
        ) -> Tuple[List[dict], int]:
        """
        Generates embeddings for the given data using the specified embedding model.

        Args:
            data_to_vectorize (str): The text data to be converted into embeddings.
            embedding_model (str, optional): The model to use for generating embeddings. Defaults to "text-embedding-ada-002".
            embedding_dimensions (int, optional): The number of dimensions for the embeddings. Defaults to 1536.

        Returns:
            Tuple[List[dict], int]: A tuple containing:
                - List[dict]: The generated embeddings.
                - int: The total number of tokens used in the embedding process.
        """
        response = self.open_ai_client.embeddings.create(
                    input=data_to_vectorize,
                    model=embedding_model,
                    dimensions=embedding_dimensions
                    )

        response_json = json.loads(response.json())

        return response_json["data"], response_json["usage"]["total_tokens"]
