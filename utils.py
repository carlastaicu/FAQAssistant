from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from database import *
import json
from data_models import *
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

#--------------------------connections and keys
llm = ChatOpenAI(
  api_key="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",
  model="gpt-4o-mini", 
  temperature=0.7
)

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# embeddings_model = OpenAIEmbeddings(
#     api_key="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",
#     model="text-embedding-3-large"
  # )

#--------------------------creating an AI Router using LangChain to route the system depending on the question
structured_llm = llm.with_structured_output(RouteQuery)
router_prompt = """
  You are an expert at routing a user question - you need to decide whether the question is related to user account settings or is a non-IT question.
  Based on the question type, route it to "it_related" if it is relevant to account settings, otherwise route it to "compliace_agent"
  
  Here is the question: "{question}"
  
  Return your response as a JSON object with a field "datasources" that contains the relevant categories as a list.
  """
router_template = PromptTemplate(input_variables=["question"], template=router_prompt)
router_chain = LLMChain(llm=llm, prompt=router_template)


def is_question(text: str) -> bool:
    # Check if the text ends with a question mark and contains at least two words
    text = text.strip()
    return text.endswith("?") and len(text.split()) >= 2

def route_question(question, question_embeddings, questions, answers):
    try:
      routing_response = router_chain.invoke({"question": question})
      parsed_response = json.loads(routing_response['text'].strip('```json\n').strip('\n```'))
      
      if "it_related" in parsed_response["datasources"]:
          # Route to the IT-related answer (i.e., account settings)
          return get_answer(question, question_embeddings, questions, answers)  
      else:
          # Route to the compliance agent with a default message
          return AnswerResponse(
              source='compliance_agent',
              matched_question='N/A',
              answer="This is not really what I was trained for, therefore I cannot answer. Try again."
          )
    except Exception as e:
        print(f"Error in OpenAI integration when routing the question: {e}")
        raise Exception("Error while querying OpenAI to route the question. Please try again later.")
      
def get_answer(query, question_embeddings, questions, answers):
    try:
      query_embedding = embeddings_model.embed_query(query)
      
      # Compute cosine similarity between query embedding and each stored question embedding
      similarities = cosine_similarity([query_embedding], question_embeddings).flatten()
      
      # Find the index of the highest similarity score
      best_match_index = np.argmax(similarities)
      best_similarity_score = similarities[best_match_index]
      print("Best similarity score: ", best_similarity_score)
      
      # Check if the best similarity score is below the threshold (0.65), if so, send it to OpenAI
      if best_similarity_score < 0.65:
          return ask_openai_question(query)
      
      return AnswerResponse(
            source='local',
            matched_question=questions[best_match_index],
            answer=answers[best_match_index]
          )
      
    except Exception as e:
        print(f"Error in get_answer: {e}")
        raise ValueError("There was an error while processing the embeddings or query.")

def ask_openai_question(question):
    try:
        prompt = f"""
          Answer the following question in a paragraph-style, consice and general explanation in full sentences.
          
          Question: {question}
          """
        
        response = llm.invoke(prompt)
        
        return AnswerResponse(
          source='openai',
          matched_question='N/A',
          answer=response.content
        )

    except Exception as e:
        print(f"Error in OpenAI integration: {e}")
        raise Exception("Error while querying OpenAI. Please try again later.")
