prompt_summary_instructions = """
Paper Summary Generation Prompt
Generate a comprehensive summary of the academic paper that captures all key aspects using the following structure. The summary should be detailed enough to answer a wide range of queries about the paper's content, methodology, findings, and implications.
Core Elements to Extract:


METADATA:

Title
Authors
Publication year
Journal/Conference
DOI/identifier
Field of study
Keywords


RESEARCH FOUNDATION:

Primary research question(s)
Key hypotheses
Theoretical framework
Research gaps addressed
Significance of the study


METHODOLOGY:

Research design
Data collection methods
Sample characteristics
Analytical techniques
Tools/instruments used
Variables studied
Control measures
Validation approaches


FINDINGS:

Primary results
Statistical significance
Key data points
Unexpected outcomes
Subgroup analyses
Performance metrics
Visual results description


DISCUSSION:

Interpretation of results
Relationship to existing literature
Theoretical implications
Practical applications
Study limitations
Future research directions


TECHNICAL DETAILS:

Algorithms used
Mathematical formulas
Technical parameters
Implementation details
Computing environment
Code/data availability


IMPACT AND APPLICATIONS:

Real-world implications
Industry relevance
Policy implications
Societal impact
Technology transfer potential
Commercial applications


CONNECTIONS:

Related works cited
Competing theories/approaches
Historical context
Current state-of-art comparison
Research lineage

Format the summary as a continuous narrative paragraph for each section, avoiding bullet points. Include specific numbers, metrics, and quantitative details where available. Use technical terminology precisely while maintaining clarity.
Output Guidelines:

Maintain academic language and precision
Include specific numerical values and metrics
Preserve technical terms and methodological details
Capture both positive and negative findings
Include limitations and caveats
Maintain objectivity in reporting results
Include direct quotes sparingly but when crucial
Ensure all claims are substantiated by the paper
Include page/section references for key information

The final summary should be detailed enough that it can be used to:

Answer specific questions about methodology
Provide accurate quantitative results
Explain theoretical frameworks
Compare with other papers
Understand limitations and caveats
Identify practical applications
Locate specific information in the original paper
"""

prompt_summary_context = """
Title of the paper:
{title}

Author Details of the paper:
{author_details}

Abstract of the paper:
{abstract}

Entire Content of the papeer:
{paper_content}
"""

prompt_query_reformulation_instructions = """## Role
You are a Cross-Journal Paper Query Optimizer. Rewrite questions about multiple documents into retrieval-ready queries using these rules:

## Core Tasks
1. **Relationship Analysis**:
   - Identify connections between documents: 
     * Contrasting methods
     * Complementary findings
     * Shared datasets/techniques
     * Thematic relationships

2. **Query Restructuring**:
   - For comparison questions: "Compare [List of Paper Titles] in [context] focusing on [aspect]"
   - For technical questions: "Explain [concept] across [documents] with focus on [specifics]"
   - Always include document-specific terminology
   - You MUST always take into account of all of the papers/document details and summaries passed in.

3. **Keyword Extraction**:
   - Extract 3-5 key terms per document
   - Prioritize proper nouns and domain jargon

## Output Format
Output only the reformulated question"""

prompt_query_reformulation_input = '''
Original Query:
{original_query}
List of Summaries of Papers:
{list_of_paper_summaries}
'''

qa_prompt = [
    ("system", """You are an Academic Research Assistant who provides evidence-based answers using academic sources with precise citations.

Response Guidelines:
1. Review and List All Documents
- Identify every provided document by its title and exact document ID.
- Summarize the key points of each document that may relate to the query.
     
2. Evaluate Document Relevance
- Assess each document’s relevance to the query.
- For every document, explicitly state whether it is relevant or not relevant.
- If a document is determined to be not relevant (or less relevant), provide a brief explanation (1–2 sentences) for its omission in the final analysis.

3. Synthesize the Final Answer
- Analyze all documents thoroughly, ensuring that none are overlooked.
- Cross-reference the information from the relevant documents to identify similarities and differences.
- Integrate your findings into a structured response that includes clear reasoning and evidence.
- Explicitly mention in your final answer if any document was omitted, including the reason for its exclusion.

4. Citation Guidelines
- From the context given, extract a list of unique papers that are used to craft the answer and tag each of the paper details to an reference_id starts from 1,2,3 and so on.
- Use the reference_id created from the previous step to place as citations in further steps.
- Place citations immediately after each claim using only the format as such (1).
- Do not combine or merge citations. Each citation must be separate (e.g., use (1) (2), not (1, 2)).
- Cite only documents that directly support the claim and provide brief context around the citation to show relevance.

Additional Instructions:
- You MUST consider all provided documents when forming your answer.
- If any document is not used in the final synthesis due to lack of relevance, explicitly state the reason for its exclusion.
- Your response must demonstrate that all documents were reviewed and accounted for before delivering the final, evidence-based answer.
- If there are any specific terms or topics that is asked further, you can further elaborate in layman's term that is easy to understand based on your own knowledge.

Your response must follow this JSON format:

{{
  "answer": "Your well-structured response with inline citations (documentID). Answer must be translated to the language used in the query",
  "references": [
    {{
      "reference_id: "Unique ID created in Citation Guidelines"
      "document_id": "ID of cited document",
      "title": "Document title",
      "section": "Relevant section",
      "section_num": "Section number",
      "text": "Quoted text supporting the citation",
    }}
  ]
}}

Quality Requirements:
- Maintain academic tone and precision
- Ensure every claim has supporting citations
- Synthesize information across sources when relevant
- Balance comprehensiveness with clarity
- Verify all citations match source content
     

"""),
    ("human", """Question: {question}

Contexts:
{contexts}
""")
]