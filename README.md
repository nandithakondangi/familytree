# Family Tree Visualizer

## 1. Introduction

This document outlines the requirements for a personal software project: a family tree application designed to help users visualize and understand complex familial relationships.

### 1.1 Purpose

The Family Tree Visualizer is designed to help users create, visualize, and understand their family connections. It aims to address the challenge of identifying and remembering relatives, especially within large families. A key goal is to be adaptable to different cultural contexts, allowing users to record and view information relevant to their heritage.

### 1.2 Goals

* Provide a user-friendly interface for exploring family connections.
* Enable users to quickly identify relationships between individuals.
* Facilitate the sharing of family tree data with others.
* Preserve and document family history for future generations.
* Support both general family tree information and culture-specific details.

### 1.3 Target User

This application is for:

* Individuals who want to better understand and visualize their extended family relationships.
* People who struggle to remember the connections between relatives, especially in large families.
* Users interested in documenting and preserving their family history.
* Users from diverse cultural backgrounds with varying needs for family data.

## 2. Background and Motivation

### 2.1 Problem Statement

In large families, it is often challenging to keep track of the precise relationships between numerous relatives. This can lead to awkward situations, such as not recognizing a relative or being unable to explain how two people are related. Additionally, different cultures have different important family data that standard tools may not accommodate.

### 2.2 Motivation

This project is born from the developer's personal experience:

> "In a large Indian family, it's hard to keep track of who is related to whom. I might know a person by name, but won't know how they are related. This becomes especially hard when someone in a function asks, 'Do you remember who I am?' I want to be in a position to come back and check who this is, and find relationship details and any other info to help me remember them."

The desire is to create a tool that can provide quick access to this information, improve social interactions within the family, preserve family history, and be useful for a wider audience by incorporating cultural adaptability.

## 3. Scope

### 3.1 In Scope

* **Visualization:** Tree-like structure for family relationships.
* **Interactive UI:** Clickable nodes to display individual details, modern interface.
* **Relationship Display:** Show immediate family members (parents, siblings, spouse, children) for a selected individual.
* **Navigation:** Pan and zoom functionality for large family trees.
* **Data Storage:** Use Protocol Buffers (protobuf) for efficient data storage.
* **Data Exchange:**
    * Ability to export a portion of the family tree.
    * Ability to import a portion of a family tree and merge it with existing data.
* **Cultural Customization:**
    * Inclusion of cultural settings to show/hide culture-specific data.
    * Inclusion of traditional Indian household-specific data (e.g., star birth date, thithi for death anniversaries) when Indian culture setting is enabled.
* **Personal Details:**
    * Inclusion of a nickname for a family member.
    * Inclusion of a map to hold any additional, custom data.

### 3.2 Out of Scope (for now)

* Automated data entry from external sources (e.g., genealogical databases).
* Advanced search functionality beyond direct relationship tracing.
* User authentication and access control.
* Mobile application development (initially).
* User-defined culture-specific data fields (may be a future enhancement).

## 4. Features

### 4.1 Core Features

* **4.1.1 Family Tree Visualization:**
    * Dynamic, interactive visualization of family relationships.
    * Clear representation of individuals and their connections.
    * Modern UI.
* **4.1.2 Individual Details:**
    * Clickable nodes in the tree to display detailed information about a person.
* **4.1.3 Relationship Highlighting:**
    * Highlighting of direct relationships (parents, siblings, spouse, children) for a selected individual.
* **4.1.4 Immediate Family View:**
    * Display of an individual's immediate family (parents, siblings, spouse, and children).
* **4.1.5 Navigation:**
    * Pan and zoom functionality for navigating large family trees.
* **4.1.6 Data Storage:**
    * Storage of family tree data in protobuf format.
* **4.1.7 Data Exchange:**
    * Export a selected portion of the family tree data.
    * Import a portion of a family tree and merge it with the existing data.
* **4.1.8 Cultural Settings:**
    * Ability to select a culture (e.g., Indian, General).
    * Display of culture-specific fields is conditional based on the selected culture.
* **4.1.9 Traditional Indian Family Details:**
    * Inclusion of fields for:
        * Star birth date based on a version of Indian calendar.
        * Thithi for death anniversaries (for tracking Shraddhams).
    * These fields are only displayed when the Indian culture setting is enabled.
* **4.1.10 Additional Personal Details:**
    * Inclusion of fields for:
        * Nickname.
        * Additional data (map for custom key-value pairs).

## 5. User Stories (Customer Use Journeys)

### 5.1 Core User Journeys

* **Viewing a Relative's Details:** As a user, I want to be able to click on a person in the family tree to see their name, birthdate, and relationship to me, so I can quickly recall who they are.
* **Understanding a Relationship:** As a user, I want to select a person in the family tree and see their direct relatives highlighted, so I can easily understand how they are connected to others in the family.
* **Navigating the Family Tree:** As a user, I want to be able to pan and zoom the family tree, so I can navigate large family structures and find the person I am looking for.
* **Sharing Family Information:** As a user, I want to be able to export a portion of the family tree, so I can share information about a specific branch of my family with other relatives.
* **Incorporating External Data:** As a user, I want to be able to import a portion of a family tree, so I can merge information from other relatives into my own family tree data.
* **Viewing Cultural Details:** As a user, I want to be able to select a culture and view the relevant culture-specific details for each individual.
* **Viewing Traditional Indian Family Details:** As a user, when the Indian culture setting is enabled, I want to be able to view traditional Indian family details such as star birth date, thithi for death anniversaries, for each individual.
* **Viewing Additional Personal Details:** As a user, I want to be able to view additional personal details such as nickname and other custom data for each individual, so I can record and access a wider range of information.

## 6. Technical Requirements

* **Data Model:**
    * Utilizes **Protocol Buffers (protobuf)** for schema definition and data storage.
    * Schema includes fields for: Name, Birthdate, Relationship to ego, Culture (enum: GENERAL, INDIAN), Star birth date (optional), Thithi for death anniversaries (optional), Gothram, Nickname, Additional data (map<string, string>).
    * Display of optional fields like "Star birth date" and "Thithi" is controlled by the selected culture.
* **User Interface:**
    * Modern and dynamic web-based UI.
    * Interactive elements: clickable nodes, pan/zoom.
    * Culture selection settings.
    * Conditional display of fields based on culture.
* **Platform:**
    * Web-based application (initial focus).
* **Performance:**
    * Fast loading times.
    * Efficient handling of large family trees.
* **Maintainability:**
    * Well-structured and documented codebase.

## 7. Success Criteria

* **Usability:**
    * Easy navigation and information retrieval.
    * Intuitive interface.
    * Simple culture selection and data display.
* **Performance:**
    * Quick load times and smooth interactions.
    * Handles large datasets effectively.
* **Data Integrity:**
    * Accurate and consistent data storage.
    * Reliable import/export functionality.
* **Adoption:**
    * Used by the developer's family members.
    * Appeals to users from diverse cultural backgrounds.
* **Completeness of Information:**
    * Ability to record and view all relevant family details, including culture-specific data, nicknames, and custom information.

## 8. Future Considerations

* User authentication and access control.
* Mobile application development.
* Integration with other genealogical data sources.
* Advanced search and filtering capabilities.
* Collaboration features for multiple users to edit the family tree.
* Support for user-defined culture-specific fields.

## Getting Started

To get the Family Tree Visualizer up and running, follow these steps:
 
1.  **Install `uv` (Standalone Installer):** `uv` is a fast Python package installer and runner.

    *   **Linux and macOS:**
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    *   **Windows (PowerShell):**
        ```powershell
        irm https://astral.sh/uv/install.ps1 | iex
        ```

    For other installation methods or troubleshooting, refer to the official `uv` installation guide.

    *If you previously installed `uv` skip this step*

2.  **Navigate to the Project Directory:** Open your terminal or command prompt and change your current directory to the root of the `familytree` project where this `README.md` file is located.

    ```bash
    cd /path/to/your/familytree/project
    ```

3.  **Run the Application:** Use `uv` to run the main application script. `uv run` will automatically create a virtual environment if one doesn't exist, install the project's dependencies (defined in `pyproject.toml`), and then execute the specified script.

    ```bash
    uv run familytree/family_tree_app.py
    ```

    This command will start local application using pyside6. 

<!-- 4.  **Access the Application:** Open your web browser and go to the address displayed in your terminal (usually `http://127.0.0.1:5000/` or `http://localhost:5000/`). -->

You should now see the Family Tree Visualizer interface.


### Chatbot Setup (Optional)

This application includes an optional chatbot feature powered by Google Gemini to answer questions about the loaded family tree. To use the chatbot, you need a Google AI Studio API key.

**Security:** Your API key is **not** stored in the application code or shared. It is read from an environment variable on your system.

**Steps:**

1.  **Get an API Key:** Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Set Environment Variable:** Before running the application, set the `GOOGLE_API_KEY` environment variable to your key.

    *   **Linux/macOS:**
        ```bash
        export GOOGLE_API_KEY='YOUR_API_KEY_HERE'
        # Then run the application from the same terminal
        python family_tree_app.py
        ```
        (To make it permanent, add the `export` line to your shell profile file like `.bashrc`, `.zshrc`, etc.)

    *   **Windows (Command Prompt):**
        ```cmd
        set GOOGLE_API_KEY=YOUR_API_KEY_HERE
        # Then run the application from the same command prompt
        python family_tree_app.py
        ```

    *   **Windows (PowerShell):**
        ```powershell
        $env:GOOGLE_API_KEY = 'YOUR_API_KEY_HERE'
        # Then run the application from the same PowerShell window
        python family_tree_app.py
        ```
        (For permanent setting on Windows, search for "Environment Variables" in system settings.)

3.  **Run the Application:** Start the Family Tree application. The chatbot interface should now be functional. If the key is not found, you will see a warning message.

**Note:** The chatbot's knowledge is limited to the summary of the family tree provided to it in the prompt. For very large trees, the summary might be truncated.

## Contributing

*(Guidelines for contributing to the project will be added here.)*

## License

*(License information will be added here.)*