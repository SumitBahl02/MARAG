from langchain.text_splitter import RecursiveCharacterTextSplitter #type: ignore
from langchain_community.document_loaders import WebBaseLoader#type: ignore
from langchain_community.vectorstores import Chroma#type: ignore
from langchain_openai import OpenAIEmbeddings#type: ignore
from langchain_core.prompts import ChatPromptTemplate#type: ignore
from langchain_openai import ChatOpenAI#type: ignore
from pydantic import BaseModel, Field#type: ignore
from typing import Literal, List
from typing_extensions import TypedDict
from langchain.schema import Document#type: ignore
from langchain import hub#type: ignore
from langchain_core.output_parsers import StrOutputParser#type: ignore
from langchain_community.tools.tavily_search import TavilySearchResults#type: ignore
from langgraph.graph import END, StateGraph, START#type: ignore
from pprint import pprint
import os
from dotenv import load_dotenv#type: ignore
from langchain.tools import StructuredTool
from llama_index.retrievers.pathway import PathwayRetriever
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import PathwayVectorClient
load_dotenv()

os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY"

client = PathwayVectorClient(
    url="http://172.30.2.194:8767",
)


llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
load_dotenv()
# Set embeddings
embd = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# retriever = vectorstore.as_retriever()
retriever = PathwayRetriever(url="http://172.30.2.194:8767", similarity_top_k=10)

# query =  """Markdown Table business segment with least growth contribution"""
query = "Markdown Table If we exclude the impact of M&A, which segment has dragged down 3M's overall growth in 2022?"
# 2021 2022 performance by business segment 3M Company"""
print(client.similarity_search_with_score(query,metadata_filter =r"contains(path,`3M_2022`)"))
# print(client.similarity_search(query))
# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

# LLM with function call


structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to SEC fillings of multiple companies.
Use the vectorstore for questions on these topics. Otherwise, use web-search."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router
print(
    question_router.invoke(
        {"question": "Who will the Bears draft first in the NFL draft?"}
    )
)
print(question_router.invoke({"question": "What are the types of agent memory?"}))

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

# LLM with function call


structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
# question = "agent memory"
# docs = retriever.invoke(question)
# doc_txt = docs[1].page_content
# print(retrieval_grader.invoke({"question": question, "document": doc_txt}))

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
# generation = rag_chain.invoke({"context": docs, "question": question})
# print(generation)

# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# LLM with function call


structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# Prompt
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader
# hallucination_grader.invoke({"documents": docs, "generation": generation})

# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

# LLM with function call


structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_grader
# answer_grader.invoke({"question": question, "generation": generation})

# LLM



# Prompt
system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | llm | StrOutputParser()
# question_rewriter.invoke({"question": question})

web_search_tool = TavilySearchResults(k=3,tavily_api_key=os.getenv("TAVILY_API_KEY"))

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
        count: Number of times retriever is called
    """

    question: str
    generation: str
    documents: List[str]
    count: int


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]
    count = state["count"]+1
    
    # Retrieval
    documents = retriever.retrieve(question)
    for doc in documents:
        print(doc.to_dict()['node']['class_name'])
        print('==================================')
    documents = [doc.text for doc in documents]
    return {"documents": documents, "question": question, "count":count}

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        # page_content = ' '.join(doc.text for doc in d)
        # page_content = d[0].text
        # print(page_content)
        print(d)
        print('---------------------------')
        score = retrieval_grader.invoke(
            {"question": question, "document": d}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    print("better_question: ", better_question)
    print("#####################################")
    return {"documents": documents, "question": better_question}

def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question}


class RewrittenQueries(BaseModel):
    """Possible queries for a given user question."""

    query1: str = Field(
        description="Rewritten query number 1"
    )
    query2: str = Field(
        description="Rewritten query number 2"
    )
    query3: str = Field(
        description="Rewritten query number 3"
    )
    query4: str = Field(
        description="Rewritten query number 4"
    )
    query5: str = Field(
        description="Rewritten query number 5"
    )


structured_llm_rewriter = llm.with_structured_output(GradeDocuments)


# Prompt
system = """You are an expert at rewriting a user question for querying a vectorstore or web search.
The database contains documents related to SEC fillings of multiple companies and other financial documents.
Your task is to generate multiple rephrased queries for the user question to improve search results.
While rewriting queries remember that the query text need to closely match the content of the documents in the database for vector store search.
Output 5 rephrased queries for the user question.
"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router
print(
    question_router.invoke(
        {"question": "Who will the Bears draft first in the NFL draft?"}
    )
)

def possible_queries(state):
    """
    Generate possible queries from the user question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a list of possible queries
    """

    print("---POSSIBLE QUERIES---")
    question = state["question"]
    response = client.chat.completions.create(
                    messages=[{
                    "role": "user",
                    "content": f"For the following query, {question}, generate possible queries for searching financial data. Keep in mind that a lot of the data may be similar which may filter out due to similarity matching retrieval. Try to generate queries that are different from each other and target specific sections of a financial document such as SEC fillings.",
                    }],
                    model="gpt-4o-mini",
                    )
        # print('Raw Response:\n',response)
    rephrased =  response.choices[0].message.content.strip()

    # Generate possible queries
    possible_queries = []
    # possible_queries.append(question)
    # possible_queries.append(question + " financials")
    # possible_queries.append(question + " SEC filings")
    # possible_queries.append(question + " financial performance")
    # possible_queries.append(question + " financial reports")

    return {"question": possible_queries}


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    state["count"] = 0
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    # return "vectorstore"

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:  #--------------------------------------------------------------------------------------
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"

# added (new)
def decide_after_transform(state):
    print("---ASSESS TRANSFORMED QUERY DOCUMENTS---")
    filtered_documents = state["documents"]

    if not filtered_documents and state["count"] >= 2 :
        # All documents have been filtered, try web search
        print("---DECISION: ALL DOCUMENTS ARE STILL NOT RELEVANT TO QUESTION, PERFORM WEB SEARCH---")
        return "web_search"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: RETRIEVE---")
        return "retrieve"





def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


# ======================================================================================================
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae
workflow.add_node("transform_query", transform_query)  # transform_query

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)


# new =================================================
workflow.add_conditional_edges(
    "transform_query",
    decide_after_transform,
    {
        "web_search": "web_search",
        "retrieve": "retrieve",
    },
)

# workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)



# Compile
app = workflow.compile()

class DataNode(BaseModel):
    query: str = Field(description="The Query to be processed for fetching data")


def data_node_function(query: str) -> str:
    """
    An LLM agent with access to a structured tool for fetching internal data or online source.
    """
    inputs = {
        "question": query,
        "count": 0,  # Add this line to initialize count
        "documents": [],  # Add this line to initialize documents
        "generation": ""  # Add this line to initialize generation
    }
    results =  app.invoke(inputs)
    return results['generation']
    # for output in app.stream(inputs):
    #     for key, value in output.items():
    #         # Node
    #         pprint(f"Node '{key}':")
    #         # Optional: print full state at each node
    #         # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
    #     pprint("\n---\n")
    # Final generation
    # pprint(value["generation"])


data_node_tool = StructuredTool.from_function(
    data_node_function,
    name="data_node_tool",
    description="""data_node_tool(query: str) -> str:
    An LLM agent with access to a structured tool for fetching internal data or online source.
    Use it whenever you need to fetch internal data or online source.
    Provide concise queries to this tool, DO NOT give vague queries like
    - 'What was the gdp of the US for last 5 years?'
    - 'What is the percentage increase in Indian income in the last few years?'
    Instead, provide specific queries like
    - 'GDP of the US for 2020'
    - 'Income percentage increase in India for 2019'
    ALWAYS mention units for searching specific data wherever applicable and use uniform units for an entity accross queries.
    Eg: Always use 'USD' for currency,'percentage' for percentage, etc.
    ALWAYS provide specific queries to get accurate results.
    DO NOT try to fetch multiple data points in a single query, instead, make multiple queries.
    """,
    args_schema=DataNode,
)
# Run

# print('___________________________________________')
# print(data_node_tool.invoke({"query": "What is GDP of India and USA. What is the difference between two. What is the precentage increase in their GDPs"}))

# inputs = {
#     "question": "Who is narendra modi",
#     "count": 0,  # Add this line to initialize count
#     "documents": [],  # Add this line to initialize documents
#     "generation": ""  # Add this line to initialize generation
# }
# for output in app.stream(inputs):
#     for key, value in output.items():
#         # Node
#         pprint(f"Node '{key}':")
#         # Optional: print full state at each node
#         # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
#     pprint("\n---\n")

# # Final generation
# pprint(value["generation"])

# Run
# inputs = {"question": "What are the types of agent memory?"}
# for output in app.stream(inputs):
#     for key, value in output.items():
#         # Node
#         pprint(f"Node '{key}':")
#         # Optional: print full state at each node
#         # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
#     pprint("\n---\n")

# # Final generation
# pprint(value["generation"])