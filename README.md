## Spotify Local Environment Variables

To configure your local environment variables for this project, you'll need to create a `.env` file in the project's root directory. This file will hold sensitive information that shouldn't be shared publicly, which is why it's included in the `.gitignore` file.

Follow these steps to set it up:

1. Begin by creating a `.env` file in the root directory of your project.
2. Locate the `env-sample` file within the project. This file provides a template for the environment variable declarations required for the application to function.
3. Copy all the contents from the `env-sample` file.
4. Paste the copied contents into your `.env` file that you just created.
5. Substitute the placeholder values (`xxxx`) with your actual credentials. For instance, you'll need to input your Spotify `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` as specified in your Spotify developer dashboard.

Below is an example of how your `.env` file should look once you've entered your details:

## Python Environment and Flask Setup
Before launching your application, it's crucial to install all required Python packages. Utilizing a virtual environment is recommended for managing project dependencies efficiently. Follow these steps to prepare and activate a virtual environment:

For Windows users:
1. If not already installed, install `virtualenv` using the following command:
   
Additionally, ensure all necessary Python packages are installed by running:
pip install virtualenv
virtualenv venv
venv\Scripts\activate

2. Once the virtual environment is activated, install the necessary packages by running the command:
   
pip install -r requirements.txt

This will install Flask, python-dotenv, and requests as specified in your `requirements.txt` file.

