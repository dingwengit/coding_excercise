# Quickstart

This project is based on Python 3 (v3.6) and tested on Mac Pro laptop.

## To run the program
* python main.py -i playlist.json -c playlist_change.csv -o playlist_output.json
* main class is in playlists.py

## Design for Scalability

* Input JSON File
  * For a very large input file, loading entire json file into memtory is not possible. 
    The program is designed to parse the input string line-by-line.
  * Next for each playlist json, apply the changes of change_file if the user_id matches in change_file 
  * Then convert each updated playlist json object into string and writes to output file

* Change file
  * format of change file is in CSV format, for example
    * "object", "action", "user_id", "song_ids"
    * song,remove,7, 3, 4, 5
    * playlist, add,6,4,5,3
    * song,add,2,8,32,2 
  * read the CSV file line-by-line, and save the changes into 3 hashtables, where key is user_id, values are song_ids
    * the sequence of changes for any user_id are considered, and merged into the above 3 hashtables for a given user_id 
  * after reading all the lines in the change file, we can apply the changes using the 3 hashtables on each playlist for a given user's playlist in input_file
    
* validation of user_id and song_id in change_file
  * each change in change file has user_id, and song_ids, we need to make sure that these ids are present in input_file 
  * the program first go through the entire input file to collect these user_ids and song_ids into 2 set objects, then we can use the set objects to validate the ids in each change