from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

class EnhancedQAChain:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )
        self._setup_chains()
    
    def _setup_chains(self):
        """Setup the question answering chains"""
        # Rephrase chain
        rephrase_template = """Given the following question, rephrase it as a clear, concise statement of what the user is asking about. Keep it under 15 words and make it sound natural.

Original question: {question}
Rephrased: """
        
        self.rephrase_prompt = PromptTemplate(
            input_variables=["question"],
            template=rephrase_template
        )
        self.rephrase_chain = LLMChain(llm=self.llm, prompt=self.rephrase_prompt)
        
        # QA chain
        qa_template = """You are a helpful AI assistant that answers questions based ONLY on the provided document context.

Context: {context}

Question: {question}

Instructions:
- If you can answer the question using the provided context, give a comprehensive and accurate answer.
- If the question cannot be answered using the provided context, respond with EXACTLY:
  "I couldn't find relevant information for '{rephrased_question}'. Feel free to rephrase or try a different topic."
- Do not make up information not in the context.
- Do not apologize excessively or provide long explanations about your limitations.

Answer:"""
        
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question", "rephrased_question"],
            template=qa_template
        )
        self.doc_chain = load_qa_chain(self.llm, chain_type="stuff", prompt=self.qa_prompt)
    
    def __call__(self, inputs):
        """Process a question and return an answer"""
        question = inputs["question"]
        chat_history = inputs.get("chat_history", [])
        
        # Get relevant documents
        docs = self.retriever.get_relevant_documents(question)
        
        # Rephrase question
        try:
            rephrased = self.rephrase_chain.run(question=question).strip()
            rephrased = rephrased.replace('"', '').replace("'", "").strip()
            if not rephrased:
                rephrased = question
        except:
            rephrased = question
        
        # Generate answer
        try:
            result = self.doc_chain.run(
                input_documents=docs,
                question=question,
                rephrased_question=rephrased
            )
        except Exception:
            result = f'I couldn\'t find relevant information for "{rephrased}". Feel free to rephrase or try a different topic.'
        
        return {
            "answer": result,
            "source_documents": docs,
            "rephrased_question": rephrased
        }

def create_qa_chain(llm, retriever):
    """Factory function to create QA chain"""
    return EnhancedQAChain(llm, retriever)