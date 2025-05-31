c = get_config()

# Configure the notebook server to recognize our repository structure
c.ServerApp.root_dir = '.'
c.NotebookApp.notebook_dir = '.'

# Allow hidden files/folders to be visible 
c.ContentsManager.allow_hidden = True

# Default to JupyterLab interface
c.NotebookApp.default_url = '/lab'

# Trust all notebooks by default
c.NotebookApp.trust_notebooks = True

# Disable terminal access if security is a concern
# c.TerminalManager.enabled = False

# Allow all origins for API requests
c.ServerApp.allow_origin = '*'

# Set CORS headers
c.ServerApp.allow_credentials = True
