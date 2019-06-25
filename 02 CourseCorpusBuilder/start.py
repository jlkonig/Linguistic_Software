from libs import corpus_structure
from libs import corpus_annotate
from libs import corpus_analyse

print()

print("(1) Structuring the corpus")
corpus_structure.run()
print("(2) Annotating the corpus")
corpus_annotate.run()
print("(3) Analysing the corpus")
corpus_analyse.run()