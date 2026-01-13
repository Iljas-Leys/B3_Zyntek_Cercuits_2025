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