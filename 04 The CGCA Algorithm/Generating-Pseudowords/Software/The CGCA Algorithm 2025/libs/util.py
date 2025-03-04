# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Util, the CGCA Algorithm -------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# variables ----------------------------------------------------------------
# --------------------------------------------------------------------------

ERR_ARGS 		= "\nWhoops, we couldn't process your command line arguments. \n\nPlease use \"-help\" to get more information."
ERR_ARGS_FILE 	= "\nWhoops, it looks like you forgot to enter an input filename. \n\nPlease use \"-help\" to get more information."
ERR_FILE_READ	= "\nWhoops, it looks like something went wrong while reading the input file. \n\nPlease try again. Make sure you have entered the right filename"
ERR_COUNT_FORMAT= "\nWhoops, it looks like you may have entered the pseudoword count in the wrong format. Please ensure that it is a whole positive number (i.e. -c 10)"
ERR_NGRAM_FORMAT= "\nWhoops, it looks like you may have entered the n-gram sizes in the wrong format. \n\nThe size of the ngrams can be a single number (i.e. -n 3), a comma seperated list of numbers (i.e. -n 3,4,5) a range of numbers (i.e. -n 3-5) or a combination of each (i.e. -n 3-5,8). Finally, 'r' can be used to refer to r-grams (i.e. -n r). Please note, 'r' cannot be used in a range, for example, -n 2-r is not valid.The DEFAULT is 2-8,r"
ERR_PWORD_FORMAT= "\nWhoops, it looks like you may have entered the pseudoword lengths in the wrong format. \n\nThe length of the pseudowords can be a single number (i.e. -l 3), a comma seperated list of numbers (i.e. -l 3,4,5) a range of numbers (i.e. -l 3-5) or a combination of each (i.e. -l 3-5,8). Finally, 'a' can be used to refer to any length (i.e. -l a). Please note, 'a' cannot be used in a range, for example, -l 2-a is not valid.The DEFAULT is a"