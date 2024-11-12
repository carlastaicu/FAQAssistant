
# Semantic FAQ Assistant

In this README you can find all the necessary information regarding the implementation for the Semantic FAQ Assistent with its respective requirements and three additional bonus tasks (authentication, AI Router using LangChain, and Docker for running). This API allows users to authenticate and ask questions using endpoints:

* POST /token - authenticate the user and get a JWT token
* POST /ask-question - ask question once the user is authenticated; answer given from the FAQ database or from OpenAI

I started with creating a virtual environment to isolate dependencies and prevent conflicts. In the final stage, I used Docker to build an image and run the app in a container. 

### Computing Embeddings
To compute the embeddings, there is first the decision of what models to use for the given text. My initial choice was HuggingFace given the low cost (free) and the nature of the task, as the text consists of non-specialized notations. I also experimented with OpenAI embeddings using the model `text-embedding-3-large`, which can be used if uncommented. 

### Similarity Search Functionality
For computing the similarity score, I used the cosine similarity given its performance for semantic similarity. We set manually the match score thresholds (0.65) for which we switch to the OpenAI's API. The value for the threshold was chosen because of the similarity between questions by their way of phrasing i.e. the questions 'Do I have set up two-factor authentication for my account?' and 'Can I set up two-factor authentication for my account?' discuss the same topic but the start phrasing implies a difference that a lower similarity threshold would not distinct.

### OpenAI API integration
For the questions that have a low similarity score, I employed OpenAI via LangChain to address the question, together with a prompt setup to keep its answer concise and efficient as it tends to over-explain its response. 

### Authentication
I set up an JWT-based authentication using the `Depends` mechanism. The generated token after login using a hashed password is available for 30 minutes. To login, use following credentials:

`username`: `johndoe`

`password`: `secret`

### How To Use

 (Disclaimer: my laptop crashed multiple times in the process of building the Docker image so I was unable to test this functionality. However, everything was implemented to the best of my knowledge so maybe it would work on a more performant computer. If not, you can test this functionality using the command `fastapi dev main.py` after building your own virtual environment and interacting with the Swagger UI)

After cloning the repository, build the Docker image using 

``docker build -t fastapi-app .``

Then run the application using 

``docker run -d -p 8000:8000 fastapi-app``

Using the Swagger UI, go to `http://localhost:8000/docs` to test the endpoints. Log in using the previously mentioned credentials and then test the `/ask-question` endpoint. 
