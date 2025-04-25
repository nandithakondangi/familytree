## Chatbot Setup (Optional)

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
# familytree