------------------------------------
# AzureOpenAiClient

## Overview

`AzureOpenAiClient` is a Python class designed to interact with the Azure OpenAI API. It provides methods for generating chat completions, handling structured outputs using Pydantic models, and creating text embeddings.

## Features

- **Chat Completions**: Generate responses to user input using specified models.
- **Chat History**: Generate responses to user input while keeping the chat history as context for the prompt.
- **Structured Outputs**: Parse API responses into structured data using Pydantic models.
- **Embeddings Generation**: Convert text data into numerical embeddings for further analysis.

## Usage

### Initialization
The AzureOpenAiClient class includes a `keep_history` toggle that can be set to `True` to enable the retention of chat history. When enabled, the chat history is stored as a list of `Tuple[str, str]`, where each tuple contains a `(question, answer)` pair. This history is stored as an instance attribute named `chat_history`. Note that the `chat_history` attribute is specific to the instance of the class and will reset when the Python process ends or the instance is reinitialized.

By default, this toggle does not automatically include the stored history in prompts sent to the Azure OpenAI API. The inclusion of chat history in prompts is controlled by the `chat_completions` method explained below.

```python
from msftoolbox.azure.azure_open_ai import AzureOpenAiClient

client = AzureOpenAiClient(
    open_ai_key="your_api_key",
    base_endpoint="https://your_base_endpoint",
    api_version="2023-03-15-preview",
    keep_history=True # Defaults to False
)
```

### Methods
#### Chat Completions
Generate a response based on user input and system guidance.

```python
response = client.chat_completions(
    model="gpt-4o",
    system_content="The system's instructions for context",
    user_content="User's message",
    temperature=0.5,
    max_tokens=3000
)
```

#### Chat Completions with chat history
The `chat_completions` method generates a response based on the user's input, system guidance, and optionally the previous message(s) in the conversation history. The inclusion of chat history starts by setting the instance attribute `keep_chat_history` to `True` in the initialisation of the client. The inclusion of chat history in the prompt itself is controlled by the method arguments `add_history_to_prompt` and `history_depth`.

Including chat history in the prompt increases token usage, which directly impacts costs. You will be billed for:
- Tokens in the current prompt and response
- Tokens for the included chat history: Each question/answer pair added to the prompt contributes to the total token count. The number of pairs is controlled by `history_depth`.

Be mindful of these costs, particularly when using long histories or when generating responses with high token limits.

```python
response = client.chat_completions(
    model="gpt-4o",
    system_content="The system's instructions for context",
    user_content="User's message",
    add_history_to_prompt=True, 
    history_depth=1,
    temperature=0.5,
    max_tokens=3000
)
```

#### Structured Chat Completion
Send a chat completion request with structured output parsing using Pydantic models.
Refer to the documentation [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/structured-outputs?tabs=python-secure) for other options. Note that structured outputs was first introduced in API version 2024-08-01-preview.

```python

from typing import List
from pydantic import BaseModel, Field

class MessageClassification(BaseModel):
    region: str
    confidence: float = Field(description="Confidence in the location of the region (0-1)")

# Define user message and system instructions
message = "We are horrified by the recent bombing of Ahli Arab Hospital..."
system_message = "Classify each user message into one of the following regions: Middle East, Europe, North America, South America, Asia"

response = client.structured_chat_completion(
    model="gpt-4o-structured-outputs",
    user_content=message,
    system_content=system_message,
    response_format=MessageClassification
)

print(response.region)
print(response.confidence)
```

#### Create Embedding
Generate embeddings for a given text using a specified model.

```python

embeddings, total_tokens = client.create_embedding(
    data_to_vectorize="Sample text for embedding",
    embedding_model="text-embedding-ada-002"
)
```

#### Example Workflow
Chat Completion: Generate a response for user input.
Structured Output: Parse the response into structured data.
Embeddings: Convert text into embeddings for analysis.

```python

# Initialize the client
client = AzureOpenAiClient(
    open_ai_key="your_api_key",
    base_endpoint="https://your_base_endpoint"
)

# Chat completion example
response = client.chat_completions(
    model="gpt-3.5-turbo",
    system_content="Provide a summary",
    user_content="Explain the significance of AI in modern technology.",
    temperature=0.7
)

# Structured output example
class MessageClassification(BaseModel):
    region: str
    confidence: float = Field(description="Confidence in the location of the region (0-1)")

message = "Peacefull protests were condudcted in Barcelona ..."
system_message = "Classify each user message into one of the following regions: Middle East, Europe, North America, South America, Asia"

structured_response = client.structured_chat_completion(
    model="gpt-4o-structured-outputs",
    user_content=message,
    system_content=system_message,
    response_format=MessageClassification
)

# Embedding example
embeddings, total_tokens = client.create_embedding(
    data_to_vectorize="Sample text for embedding"
)
```

This class provides a robust framework for interacting with Azure OpenAI services, enabling seamless integration of AI capabilities into your applications.

--------------------
# AzureKeyvaultClient
To be done

--------------------

# AzureStorageContainerClient
To be done

--------------------