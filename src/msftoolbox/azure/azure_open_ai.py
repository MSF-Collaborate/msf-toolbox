from typing import List, Type, TypeVar, Tuple
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
        api_version: str = "2023-03-15-preview",
        keep_history: bool = False,
    ):
        """
        Initialize the AzureOpenAi with the OpenAI API key and endpoint.

        Args:
            open_ai_key (string): The API key for Azure OpenAI.
            base_endpoint (string): The base endpoint URL for Azure OpenAI.
            api_version (string): The API version to use (default is "2023-03-15-preview").
            keep_history (bool): Whether to keep a history of chat interactions (default is False).
                When True, the client will maintain the chat history as a list of Tuple (question, answer)
                in the instance attribute chat_history. This history is scoped to the instance and resets
                when the Python process ends or the instance is reinitialized.
        """
        self.open_ai_key = open_ai_key
        self.base_endpoint = base_endpoint
        self.api_version = api_version
        self.keep_history = keep_history
        self.chat_history: List[Tuple[str, str]] = []  # Stores (question, answer) pairs
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
        add_history_to_prompt: bool = False,
        history_depth: int = 1,
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
            add_history_to_prompt (bool): Whether to include chat history in the prompt (default is False).
                For this to work, enable keep_chat_history in the class instance and adjust history_depth.
                Please note that adding history to the prompt means you will be billed for the tokens of the
                history in addition to the tokens of the prompt for each new chat completion request.
            history_depth (int): Number of previous question/answer pairs to include in the prompt.
                For this to work, enable keep_chat_history in the class instance and set the method argument
                add_history_to_prompt to True.
                Please note that adding history to the prompt means you will be billed for the tokens of the
                history in addition to the tokens of the prompt for each new chat completion request.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens to generate.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty parameter.
            presence_penalty (float): Presence penalty parameter.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            dict: The response from the OpenAI API.
        """
        # Prepare the messages for the chat completion
        messages = [{"role": "system", "content": system_content}]
        
        # Add chat history to the prompt if enabled
        if add_history_to_prompt and self.chat_history:
            for question, answer in self.chat_history[-history_depth:]:
                messages.append({"role": "user", "content": f"Previous question: {question}"})
                messages.append({"role": "assistant", "content": f"Previous question: {answer}"})
        
        # Add the current user input
        messages.append({"role": "user", "content": user_content})

        # Send the request to the OpenAI API
        response = self.open_ai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            **kwargs
        )

        # Store the interaction in history if enabled
        if self.keep_history:
            # Extract the assistant's response
            assistant_response = response.choices[0].message.content
            self.chat_history.append((user_content, assistant_response))

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