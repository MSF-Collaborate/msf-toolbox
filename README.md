# MSF Toolbox

## Overview

The MSF Toolbox is a Python package designed to streamline the integration of various services such as SharePoint, Azure services, PowerBI, DHIS2 and more. This tool aims to facilitate faster development in the building of new tools and help in the automation of task. 

## MSF's Mission

Médecins Sans Frontières (Doctors Without Borders) is an international, independent medical humanitarian organization that delivers emergency aid to people affected by conflict, epidemics, natural disasters, and exclusion from healthcare.

## Context

### Usage
The toolbox is designed to simplify the interaction with multiple services, providing a unified approach and reducing errors, duplication and time spent testing code. It can easily be installed installed and implemented in any of your projects.

### Limitations
- **Scope**: The scope of this Python package will evolve and will depend on the needs of MSF. The scope is Microsoft & Azure centric and particularly useful for Data & AI related initiatives. 
- **Support**: Limited support is available; see the [SUPPORT.md](SUPPORT.md) section for more details.

### What It Does
- Provides easy-to-use and well documented classes for specific tools that are used within the context of MSF:
    - [DHIS2](https://dhis2.org/)
    - [Sharepoint](https://www.microsoft.com/nl-nl/microsoft-365/sharepoint/collaboration)
    - [Azure](https://azure.microsoft.com/)
    - [PowerBI](https://www.microsoft.com/nl-nl/power-platform/products/power-bi)
- Streamlines authentication and data access processes to these tools
- Streamlines API integration of these tools

### What It Does Not Do
- Does not replace comprehensive SDKs or APIs provided by service providers.
- Does not provide extensive customization options beyond the basic interfaces.

## Roadmap

- **Version 0.1.8**: Initial release with core functionalities.
- **Future Updates**:
  - To be determined

## Technical Details

- **Language**: Python > 3.10
- **Dependencies**: Check pyproject.toml
- **Installation**: Provide installation instructions, e.g., via pip.

```bash
pip install git+https://github.com/MSF-Collaborate/msf-toolbox.git
```

## Reporting Issues and Requests

We welcome your feedback to help improve our product. Please follow the guidelines below to report any issues or requests:

### Bug Reports

To report a bug, please include the following information:

- **Description**: A clear and concise description of the bug.
- **Steps to Reproduce**: Detailed steps to reproduce the issue.
- **Expected Behavior**: What you expected to happen.
- **Actual Behavior**: What actually happened.
- **Environment**: Include details such as operating system, browser version, etc.
- **Screenshots/Logs**: Attach any relevant screenshots or logs.

Submit your bug report by emailing [derek.loots@amsterdam.msf.org](mailto:derek.loots@amsterdam.msf.org).

### Feature Requests

For feature requests, please provide:

- **Description**: A clear and concise description of the feature.
- **Use Case**: Explain why this feature is needed and how it would be used.
- **Benefits**: Describe the benefits and potential impact on users.

Submit your feature request by emailing [derek.loots@amsterdam.msf.org](mailto:derek.loots@amsterdam.msf.org).

### Security Issues

If you discover a security vulnerability, please report it to us directly. Do not disclose it publicly until we have addressed it.

- **Description**: A detailed description of the security issue.
- **Impact**: Explain the potential impact of the vulnerability.
- **Steps to Reproduce**: If applicable, provide steps to reproduce the issue.

Contact our security team at [derek.loots@amsterdam.msf.org](mailto:derek.loots@amsterdam.msf.org).

Thank you for helping us improve!