# random-recommendation
random recommendation is the recommendation engine developed specifically for returning Machine Learning based user recommendations. For a list of queried shift ids, the recommendation api returns a list of lists of user ids, each list corresponding to one shift id. The features X considered currently are datetime objects of start, end, and date of creation of the shift. And more specifically, for each of the 3 above mentioned datetime object, we take month, week, day, hour, and dayofweek as inputs. 

Also, filters of users on the basis of whether is booked already, availability, permission combintation (requirement specific to the shift), work hours, and whether the user is on a contract at the time of the assignment. There might be a change of this in future implementations.

To use the recommend, run:

  docker build -t recommendation:latest .
  docker run -it -p 5000:5000 -v "/local/directory/for/trained_models:/app/trained_models" -e TZBACKEND_URL=url_for_tzbackend recommendation
  
When the Flask app is up and running, we can try the recommendation by providing the same oauth2 that you have for tzbackend. And make http request as follow on insomnia:

  http://.../api/ml/v1/recommendation
  
Note that it requires manager role to access the recommendation.

And the following query parameters are needed:
  1. limit, an integer value of the number of users desired. This would include both the machine learning part and random to make up the rest. Default is 10.
  2. user-id, this needs to be the manager id. 
  3. ids, this wil be the ids for the shifts of interest. ids seperated by comma is good.
  4. ml-recommend, this will be the flag for whether to use ML recommendation. 0 for off, any integer for on. Default is 0.
  5. ml_num_candidates, this will be the desired number of recommendations by machine learning. Default is 10.
  
 
