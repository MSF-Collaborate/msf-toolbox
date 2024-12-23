------------------------------------
# AzureOpenAiClient

## Overview

`AzureOpenAiClient` is a Python class designed to interact with the Azure OpenAI API. It provides methods for generating chat completions, handling structured outputs using Pydantic models, and creating text embeddings.

## Features

- **Chat Completions**: Generate responses to user input using specified models.
- **Structured Outputs**: Parse API responses into structured data using Pydantic models.
- **Embeddings Generation**: Convert text data into numerical embeddings for further analysis.

## Usage

### Initialization

```python
from yourmodule import AzureOpenAiClient

client = AzureOpenAiClient(
    open_ai_key="your_api_key",
    base_endpoint="https://your_base_endpoint",
    api_version="2023-03-15-preview"
)
```

### Methods
#### Chat Completions
Generate a response based on user input and system guidance.

```python
response = client.chat_completions(
    model="gpt-3.5-turbo",
    system_content="The system's instructions for context",
    user_content="User's message",
    temperature=0.5,
    max_tokens=150
)
```
#### Structured Chat Completion
Send a chat completion request with structured output parsing using Pydantic models.

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