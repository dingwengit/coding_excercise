# Quickstart

This project is based on Python 3 (v3.6) and tested on Mac Pro laptop.

## To run the program
* Python 3 (v3.6 or above) installed
* python main.py -i mixtape.json -c change.csv -o output.json
* main class is in playlists.py

## Design for Scalability

* Input JSON File
  * For a very large input file, loading entire json file into memtory is not possible. 
    The program is designed to parse the input string line-by-line.
  * Next for each playlist json, apply the changes of change_file if the user_id matches in change_file 
  * Then convert each updated playlist json object into string and writes to output file
  * Justification on scale out
    * memory usage: store all user_ids (4 bytes each) and song_ids (4 bytes each), assume each input_file has 500M unique user ids and 50 M unique song ids, total memory 500M x 4 + 50 x 4 = 2.2 GB
    * input file are processed line-by-line, the memory needed is only for one-playlist json object

* Change file
  * format of change file is in CSV format, for example
    * "object", "action", "user_id", "song_ids"
    * playlist, remove,2
    * playlist, add,6,4,5,3
    * song,add,2,8,32,2 
  * read the CSV file line-by-line, and save the changes into 3 hashtables, where key is user_id, values are song_ids
    * the sequence of changes for any user_id are considered, and merged into the above 3 hashtables for a given user_id 
  * after reading all the lines in the change file, we can apply the changes using the 3 hashtables on each playlist for a given user's playlist in input_file
  * Justification on memory requirement for very large change files - assume each change_file has 500M unique user_ids
    * playlist_remove: set() - items would be user_ids (4 bytes), so it is O(n) where n is the number of users, it takes memory of 500M x 4 Bytes = 2 GB 
    * playlist_add: hashtable() - keys would be user_ids, values are song_ids (avg 10 songs, 4 bytes each), so it is 500M x 44 bytes = 22 GB 
    * song_add: hashtable() - keys would be user_ids, values are song_ids (avg 10 songs, 4 bytes each), so it is 500M x 44 bytes = 22 GB 
* validation of user_id and song_id in change_file
  * each change in change file has user_id, and song_ids, we need to make sure that these ids are present in input_file 
  * the program first goes through the entire input file to collect these user_ids and song_ids into 2 set objects, then we can use the set objects to validate the ids in each change 
* TODO:
  * when a playlist is removed, I didn't recount all the remaining playlist_ids to make all the playlist_ids to be continuous integer (as in DB sequence)