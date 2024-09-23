import openai

class AzureOpenAiClient:
    def __init__(self, open_ai_key, base_endpoint, api_version="2023-03-15-preview"):
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
            api_key=self.open_ai_key,
            api_version=self.api_version,
            azure_endpoint=self.base_endpoint
        )

    def chat_completions(
        self,
        model,
        system_content,
        user_content,
        temperature=0.3,
        max_tokens=1000,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0
        ):
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
        )

        return response