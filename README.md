# KnowledgeFlow

The KnowledgeFlow chatbot system is designed to facilitate efficient information retrieval from a
knowledge base comprising academic papers. Researchers will be able to upload relevant papers, and
the system will leverage the RAG framework to understand user queries, retrieve pertinent information
from the knowledge base, and generate concise and contextualized responses. This approach not only
reduces the time spent searching through literature but also simplifies complex language and
methodologies, making research findings more accessible to a wider audience.

## Pre-requisites
### Installing GROBID

1. Firstly, go to the `backend` folder and run the commands to install GROBID and unzip it.
```
cd backend
wget https://github.com/kermitt2/grobid/archive/0.8.1.zip
unzip 0.8.1.zip
```
2. Open the extraced folder and perform the installation of the service.
```
cd grobid-0.8.1
./gradlew clean install
```

3. If you happened to encounter the error similar to:
```
Execution failed for task ':grobid-core:compileJava'.
> invalid source release: 11
```
Go to `gradle.properties` , make changes to the code as below.
```
#add
org.gradle.java.home = <your jdk directory>
#remove
org.gradle.java.installations.auto-download=false
```
4. After the installation is completed, run GROBID with the command:
```
./gradlew run
```
5. The GROBID service will be running in port 8070 that can be accessed through your localhost.

### Provisioning an API key from MongoDB, Pinecone, OpenAI API and Reranker API
MongoDB and Pinecone are essentially the representation of NoSQL database as well as vector database. Both of these services provides a free tier for POCs and testing. The same goes for OpenAI API as well as Jina.ai's Reranker API. The execution of these APIs can be viewed in the backend folder. DB folder has all the details of databases in the form of class objects, so it can be easily modified if other similar services are to be used.

LLM operations (generation and reranking) are handled in the ```llm.py``` file in ```helper``` folder.

1. Please visit [Mongo Atlas](mongodb+srv://admin:AdminKnowledgeflow123@test.akdni.mongodb.net/?retryWrites=true&w=majority&appName=test) to create a URI. The URI should look something like this:
```
mongodb+srv://admin:xxx@test.akdni.mongodb.net/?retryWrites=true&w=majority&appName=yyy
```

2. Do also visit [Pinecone](https://www.pinecone.io) to create an account to get the API Key.

3. API key from [OpenAI](https://platform.openai.com) can be generated in the API site.

4. API key for reranking can be retrieved from [Jina.ai](https://jina.ai). They provide a free access API key, but with limited calls only.

5. Kindly create a ```.env``` file in the backend directory with the names below.
```
ATLAS_URI = <your MongoDB Atlas URI>
OPENAI_API_KEY = <your OpenAI API Key>
PINECONE_API_KEY = <your Pinecone API Key>
RERANK_API_KEY = <your Jina.ai API key>
```

## Setting up the Frontend and Backend
Front-end, which is built using Sveltekit 4 + SkeletonUI v2 and the Backend, which is largely based on Python 3 and FastAPI framework has been seperated into two different folders, Front-end and Back-end. Please make sure that you have Python 3 and Node.js installed before-hand.

### Setting up the Backend
1. Setup by running the commands below.
```
## you could also create a python virtual environment
py -m venv .venv

<choose 1 - if you have created a virtual environment, else just proceed to the commands below>
source .venv/bin/activate ## if you are on mac os/linux
.venv/Scripts/activate ## if you are on windows

cd backend
pip install -r requirements.txt
```
2. Run the frontend application.
```
uvicorn app:app --reload
```

### Setting up the Frontend
1. Setup by running the commands below.
```
cd frontend
npm install . --force
```
2. Run the frontend application.
```
npm run dev
```
Then you should be good to to test out the system!

## Some things to consider
In this repo, I will be providing the quick method of generating a public and private RSA 2048 keys that will be used as the means of encrypting and decrypting the communication of password from client-side to the backend server. Do regenerate it if it is needed using the items in the ```misc``` folder

The public key should be placed in ```private/keys``` in the Frontend folder.
The private key should be place in   ```static``` folder in the Backend folder.

## Experiments
For experiments and evaluations of retrieval methods and processes that have been done in this project, please visit the ```evaluation``` folder.

