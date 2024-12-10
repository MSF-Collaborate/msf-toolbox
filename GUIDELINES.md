### General Guidelines

1. **Consistency**: Follow the established conventions throughout the project to ensure consistency across all classes and methods.
2. **Documentation**: Document each class and method with clear and concise comments, including purpose, parameters, return values, and examples where applicable.
3. **Broad applicability**: Remove components specific to your organisation and focus on contributing features which can be useful to a range of users.
4. **Testing**: Where possible, write unit tests for each class and method to ensure they work as expected and to facilitate future changes.

### Class Naming Conventions

1. **Descriptive Names**: Use descriptive names that clearly indicate the purpose of the class.
2. **PascalCase**: Use PascalCase for class names.
3. **Prefix/Suffix**: We use a consistent suffix `Client` .
4. **Avoid Abbreviations**: Unless they are widely recognized and unambiguous.

**Example**: `DHIS2MetadataClient`, `ReliefWebClient`, `GDELTClient`.

### Method Naming Conventions

1. **Descriptive Names**: Use descriptive and action-oriented names for methods that clearly indicate their functionality.
2. **snake_case**: Use snake_case for method names.
3. **Verb-Noun Structure**: Start with a verb to indicate the action. Commonly used in this project:
- add
- check
- configure
- delete
- download
- get
- list
- update
- upload
4. **Consistency**: Use consistent naming for similar methods across different classes.

**Example**: `list_reports`, `get_report`.

### Standardized Method Functionality

1. **Error Handling**: Implement consistent error handling strategies, using exceptions where appropriate.
2. **Return Values**: Clearly define and document the return values for each method. Use standardized data structures where possible. Use JSON or JSON array where possible.

### Adding New Classes

1. **Purpose Definition**: Clearly define the purpose of the class before implementation.
2. **Interface Design**: Design a clear and concise interface for the class, focusing on the primary functionalities it should provide.
3. **Separation of Concerns**: Ensure that each class has a single responsibility and that its methods are cohesive.
4. **Fail fast**: Design the code to ensure that any issues cause the software to fail immediately and clearly. During class initialization, verify authentication parameters, and validate input parameters, offering clear error messages for any invalid inputs.
5. **Module naming**: If the purpose of the module is to extract data call it `data`, else use a name describing the service interacted with. 

### Documentation and Comments

1. **Class-Level Comments**: Provide a brief description of the class, its purpose, and any important details.
2. **Method-Level Comments**: Document each method with its purpose, parameters, return values, and exceptions.
3. **Inline Comments**: Use inline comments to explain complex logic or important details.

### Version Control

1. **Branch Naming**: Use descriptive branch names that indicate the feature or fix (e.g., `feature/dhis2-api-client`).
- feature/
- improvement/
- docs/
2. **Commit Messages**: Write clear and concise commit messages that describe the changes made.
3. **Pull Requests**: Use pull requests for code reviews and ensure that all tests pass before merging. Resolve errors from SonarCloud