# laSwarm
wiki  on swarm
    
***How It Works***

There are five components to make the wikis on the swarm.

1. trigger component 

    (1) get the latest wiki dumps list from https://dumps.wikimedia.org/other/kiwix/zim/wikipedia

    (2) trigger zim to downloading status if any news update

2. downloader component

    (1) download the zim file from https://dumps.wikimedia.org/other/kiwix/zim/wikipedia

    (2) set zim file status to extracting

3. extractor component

    (1) extract the zim file to the folders

    (2) set zim file status to uploading

4. uploader component

    (1) upload all the extracted files to swarm

    (2) set zim file status to uploaded

    (3) backup the sqlite db file to swarm to make it the newest

5. server component

    (1) prepare your own bee nodes on the local system

    (2) download the latest sqlite db http://141.94.55.59:8080/api/database (if not exist on local)

    (3) run http server on local, and then can view and search wikis through your web browser. 

    (4) for none developers, you can also visit the public daemon website http://141.94.55.59:8080/


