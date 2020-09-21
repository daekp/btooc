# btooc

btooc - by the order of comment.  
I made this code at someone's request.  
Use this tool if you need to comment quickly on Naver Cafe.  

###### ※ It has not been fully developed yet.

#### Installation
```
pip install -r requirements.txt
```

#### USAGE  
```
python fcfs.py CAFEID ID PW TIME  
python fcfs.py cafeid idididid pwpwpwpw 13:00:00  
```

If you dont know CAFEID, please refer to this.  
1. Add "m" to the URL of the cafe you know.  
https://m.cafe.naver.com/joonggonara  
2. Go to any post.  
3. you can find CAFEID in URL  
https://m.cafe.naver.com/ca-fe/web/cafes/"10050146"/articles/71222331?  
CAFEID is 10050146  

#### Bugs  
1. It recognize only post that contain certain characters('■' or '□').
