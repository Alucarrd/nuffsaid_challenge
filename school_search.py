import time
from helper import read_school_csv, format_token

#config setting:
topNResult = 3
penalty_hit = .8
school_term_score = 5
city_term_score = 1

inverted_school_name = dict()
inverted_city_name = dict()


def index_school_documents(school_data_file, stop_words, special_school_type_lookup):
    """ Indexing school name and location - This is where the search will be performed upon.
        When the module's loading at the first time, it would index the data

        Args:
            school_data_file (str): The path to the school data csv
            stop_words (list of string): The stop word list we are going to discard from index and search string
            special_school_type_lookup (dictionary of string to int): special school to their integer representation we want to look for for special cases of string)

        Returns:
            root_corpus (dictionary of int to each school document in dictionary): Assigning a numerical index for faster retrieval
            inverted_school_name (dictionary of term to list of numerical id's): Inverted index of terms in school
            inverted_city_name (dictionary of term to list of numerical id's): Inverted index of terms in city
            school_type_index (dictionary of list of numerical id's): list of school that meets the special requirement

    """
    #Initialize index
    inverted_school_name = dict()
    inverted_city_name = dict()
    school_type_index = dict()  
    
    start = time.time()
    #Apply empty list into the special school index
    for index in range(len(special_school_type_lookup)):
        school_type_index[index] = []

    #Loading the school
    my_school_list = read_school_csv(school_data_file)
    
    root_corpus = dict()
    
    #Assigning numerical id to each school document
    for index in range(0, len(my_school_list)):
        root_corpus[index] = my_school_list[index]

    #Go through each school document and indexing the three indexes we need
    for index in range(0, len(root_corpus)):
        my_doc_id = index
        #indexing the city terms
        my_city_term_list = format_token(root_corpus[index]["LCITY05"])
        for word in my_city_term_list:
            if not word in inverted_city_name.keys():
                inverted_city_name[word] = [my_doc_id]
            else:
                inverted_city_name[word].append(my_doc_id)

        #indexing the school terms
        my_school_term_list = format_token(root_corpus[index]["SCHNAM05"])
        for word in my_school_term_list:
            if word not in stop_words:
                if len(word) > 1:
                    #indexing the special school terms
                    if word in special_school_type_lookup.keys():
                        school_type_index[special_school_type_lookup[word]].append(my_doc_id)

                    if not word in inverted_school_name.keys():
                        inverted_school_name[word] = [my_doc_id]
                    else:
                        inverted_school_name[word].append(my_doc_id)

    end = time.time()
    print(f"Total reindex time is {end-start} seconds")
    return root_corpus, inverted_school_name, inverted_city_name, school_type_index

#when the module's imported the fisrt time, we will reindex the data
school_file = 'school_data.csv'

#For now, we are only dropping the term "school"
stop_words = []
stop_words.append("school")

#Special school type
special_school_type_lookup = {
    "charter": 0
}
(root_corpus, inverted_school_name, inverted_city_name, school_type_index) = index_school_documents(school_file,stop_words, special_school_type_lookup )



def get_school_term_score(score_dictionary, input_lists, point_weight):
    """Go through the documents found from the terms and add the score

        args:
            score_dictionary (dictionary of int to int): score of each school (document)
            input_lists (list of list of int): list of schools found for each term
            point_weight (int): The points we add for each document found

        return:
            score_dictionary (dictionary of int to int):score board for each school identified

    """
    #Flatten the list of list for faster point calculation
    input_list = [item for sublist in input_lists for item in sublist]
   
    #Summing the points
    for item in input_list:
        if item in score_dictionary.keys():
            score_dictionary[item] = score_dictionary[item] + point_weight
        else:
            
            score_dictionary[item] = point_weight
    return score_dictionary

def get_city_term_score(score_dictionary, input_lists, point_weight):
    """Go through the documents found from the terms and add the score for the city.  
        If the term exists in the smaller city, then we will penalize it

        args:
            score_dictionary (dictionary of int to int): score of each school (document)
            input_lists (list of list of int): list of schools found for each term
            point_weight (int): The points we add for each document found

        return:
            score_dictionary (dictionary of int to int):score board for each school identified

    """

    #Find the avg size of the school found by the city term search.  If the smaller city's score will be penalized
    avg_length = get_avg_length(input_lists)

    for my_list in input_lists:
        if len(my_list) < avg_length:
            my_point_weight = point_weight * penalty_hit
        else:
            my_point_weight = point_weight
        for item in my_list:
            if item in score_dictionary.keys():

                score_dictionary[item] = score_dictionary[item] + my_point_weight
            else:
                score_dictionary[item] = point_weight
    return score_dictionary

def get_avg_length(input_lists):
    """Calculate the avg length of list of list

        Args:
            input_lists (list of list)
        Returns:
            avgerage length (float)

    """
    lengths = [len(i) for i in input_lists]
    return 0.0 if len(lengths) == 0 else (float(sum(lengths)) / len(lengths))



def is_school_type_location_search(cleaned_search_term_list):
    """ This is the special case handling.  Check to see if the search is looking for special school in this area

        Args:
            cleaned_search_term_list (list of string): normalized terms in a list

        Returns:
            is_special_search (boolean): If this current search is looking special school in an area
            cleaned_search_term_list (list of string): search terms we want to use for the search after this step
            special_school_type (int): special school type of thi search.  If it's not a special search, will return -1


    """

    #If the last term is a special school keyword, then it is a special school search
    if cleaned_search_term_list[len(cleaned_search_term_list)-1] in special_school_type_lookup.keys():
        #is special search?, remaining search term in list, index of type of school
        return (True, cleaned_search_term_list[:len(cleaned_search_term_list)-1],special_school_type_lookup[cleaned_search_term_list[len(cleaned_search_term_list)-1]] )
    return (False, cleaned_search_term_list, -1)
    
    
def school_location_search(cleaned_search_terms_list, school_type):
    """ For a special school search, user wants to find the special school in a given area.  And this function handles that

        Args:
            cleaned_search_terms_list (list of string): cleaned term after we removed the term for special school type
            school_type (int): index of special school type
        
        Returns:
            list of special school's id's (int) that meets the location search

    """
    city_result = []
    #find the schools matche the city term
    for word in cleaned_search_terms_list:
        if word in inverted_city_name.keys():
            city_result.extend(inverted_city_name[word])

    #return the intercept of special school that are in the location
    return list(set(school_type_index[school_type]) & set(city_result)) 



    
def search_schools_helper(search_terms, topNResult=3):
    """ This function is the core of the search.  It will clean up the search term, check to see if it's special search,
        calculate the score and return the top results

        Args:
            search_terms (string): search terms user use to search
            topNResult (int): top x results we want to return based on the revelancy score

        Returns:
            list of schools we want to return by their numeric id


    """

    #Cleaning up the search term into a list
    search_term_list = format_token(search_terms)
    #remove the stop word
    search_term_list = [word for word in search_term_list if word not in stop_words ]
    
    #Check to see if it's a special school to location lookup.
    (is_special_lookup, search_term_list, type_index) = is_school_type_location_search(search_term_list)
    my_special_schools = []

    #If this is a special school to location lookup, fetch for the list of schools that will be ahead of regular result
    if is_special_lookup == True:
        my_special_schools = school_location_search(search_term_list, type_index)


    #Gather the schools that matches with the school term lookup
    school_term_result = []
    for word in search_term_list:
        school_term_result.append(inverted_school_name[word])
            
    #Gather the schools that matches with the city term lookup
    city_term_result = []
    for word in search_term_list:
        if word in inverted_city_name.keys():
            city_term_result.append(inverted_city_name[word])

    #Calculating the scores 
    score_dictionary = {}
    score_dictionary = get_school_term_score(score_dictionary, school_term_result, school_term_score)
    score_dictionary = get_city_term_score(score_dictionary, city_term_result, city_term_score)

    #Score the score dictionary to return school with highest score (most relevant)
    sorted_documents_by_score = sorted(score_dictionary.items(), key=lambda x: x[1], reverse=True)

    #Prepend the special schools at the front of the list.  If this not a special school, nothing will be prepended.
    my_special_schools.extend([ document[0] for document in sorted_documents_by_score])

    return my_special_schools[:topNResult]

def search_schools(search_terms):
    """ This is the wrapper function for school search that will be called by user
        
        Args:
            search_terms (string): raw input from user

        Returns:
            N/A

    """
    #We will also calculate the search time and rounded to 4 decimal places of second
    start = time.time()
    my_top_documents = search_schools_helper(search_terms, topNResult)
    end = time.time()
    ranking =0
    print('Results for "{}" (search took: {:.4f}s)'.format(search_terms, (end-start)))
    for document in my_top_documents:
        ranking += 1
        my_document = root_corpus[document]
        print(f'{ranking}.{my_document["SCHNAM05"]}')
        print(f'{my_document["LCITY05"]}, {my_document["LSTATE05"]}')
    