This command is used to test the data with the sample data provided in this folder
```
python -m AI.benchmarks.run_baseline --reset-index --bootstrap-sample-data
```
Results are store in *baseline.json*

This command is to test with out of scope data to see if the model will make things up
```
python -m AI.benchmarks.run_baseline --questions AI/benchmarks/out_of_scope_questions.json --reset-index --bootstrap-sample-data --out AI/benchmarks/out_of_scope_results.json
```
Results are store in *out_of_scopre_results.json*


To run the *smoke.py* use 
```
python -m AI.smoke

```
The file is used to test Redis database connection, like is the database available, you create, store and retrieve vectors, can the Redis talk with the LLM.

This is the command that creates the files in storage/extracted_text and storage/metadata.
```
python -m AI.document_ingestion.ingestion
```
This deletes old vectors and starts clean.
```
python -m AI.index_storage --recreate-index
```
Semantic chunking (recommended)
```
python -m AI.index_storage --strategy semantic
```
Recursive chunking
```
python -m AI.index_storage --strategy recursive
```
Semantic search results
```
python -m AI.retrieval_real --query "ceramic substrates" --k 5
```
Raw vector KNN (no filtering)
```
python -m AI.retrieval_real --query "ceramic substrates" --k 5 --raw
```
In-scope question (should answer)
```
python -m AI.retrieval_real --query "What is the operating temperature?" --k 5 --answer
```
Out-of-scope question (should say I don’t know)
```
python -m AI.retrieval_real --query "What is the CEO's name?" --k 5 --answer
```
